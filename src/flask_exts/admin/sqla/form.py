from enum import Enum
from wtforms import validators
from sqlalchemy import inspect
from sqlalchemy import select
from sqlalchemy import Boolean, Column
from wtforms.fields import HiddenField
from wtforms.fields import DateTimeLocalField as DateTimeField
from ...forms.fields import Select2Field
from ...forms.fields.ajax_select import AjaxSelectField
from ...forms.fields.ajax_select import AjaxSelectMultipleField
from ...forms.fields.sqla import QuerySelectField
from ...forms.fields.sqla import QuerySelectMultipleField
from ...forms.fields.sqla import InlineModelFormListField
from ...forms.fields.sqla import InlineModelOneToOneField
from ...forms.fields.inline import InlineFormField
from ...forms.form.base_form import BaseForm
from ...forms.validators.sqla import Unique
from ..model.form import BaseFormFieldConverter
from ..model.form import InlineModelConverterBase
from .query import Query
from .ajax import create_ajax_loader
from .form_converters import BasicFieldConverter, TemporalFieldConverter, SpecialFieldConverter
# 导入内联模型转换器
from .form_inline import InlineModelConverter, InlineOneToOneModelConverter


class FieldPlaceholder:
    """
    Field placeholder for model convertors.
    """

    def __init__(self, field):
        self.field = field


def convert_form_field(*args):
    def decorator(func):
        func._converter_for_form_field = args
        return func

    return decorator


# 使用 Mixin 组合优化 FormConverter
class FormConverter(BasicFieldConverter, TemporalFieldConverter, SpecialFieldConverter, BaseFormFieldConverter):
    """
    SQLAlchemy model to form converter

    使用 Mixin 组合优化代码结构，将字段转换方法分离为不同的关注点。
    - BasicFieldConverter: 基础字段类型（字符串、整数、小数等）
    - TemporalFieldConverter: 时间相关字段（日期、时间、日期时间）
    - SpecialFieldConverter: 特殊字段（枚举、JSON）
    """

    def __init__(self, session, view):
        super().__init__()

        self.session = session
        self.view = view

    def _get_label(self, name, field_args):
        """
        Label for field name. If it is not specified explicitly,
        then the views _prettify_name method is used to find it.

        :param field_args:
            Dictionary with additional field arguments
        """
        if "label" in field_args:
            return field_args["label"]

        column_labels = getattr(self.view, "column_labels", None)

        if column_labels:
            return column_labels.get(name)

        return name.replace("_", " ").title()

    def _get_description(self, name, field_args):
        if "description" in field_args:
            return field_args["description"]

        column_descriptions = getattr(self.view, "column_descriptions", None)

        if column_descriptions:
            return column_descriptions.get(name)

    def _model_select_field(self, prop, multiple, remote_model, **kwargs):
        loader = getattr(self.view, "_form_ajax_refs", {}).get(prop.key)

        if loader:
            if multiple:
                return AjaxSelectMultipleField(loader, **kwargs)
            else:
                return AjaxSelectField(loader, **kwargs)

        if "query_factory" not in kwargs:
            kwargs["query_factory"] = (
                lambda: self.session.execute(select(remote_model)).scalars().all()
            )

        if multiple:
            return QuerySelectMultipleField(**kwargs)
        else:
            return QuerySelectField(**kwargs)

    def _convert_relation(self, name, prop, kwargs):
        # Check if relation is specified
        form_columns = getattr(self.view, "form_columns", None)
        if form_columns and name not in form_columns:
            return None

        remote_model = prop.mapper.class_
        column = prop.local_remote_pairs[0][0]

        # If this relation points to local column that's not foreign key, assume
        # that it is backref and use remote column data
        if not column.foreign_keys:
            column = prop.local_remote_pairs[0][1]

        kwargs["label"] = self._get_label(name, kwargs)
        kwargs["description"] = self._get_description(name, kwargs)

        # determine optional/required, or respect existing
        requirement_options = (validators.Optional, validators.InputRequired)
        requirement_validator_specified = any(
            isinstance(v, requirement_options) for v in kwargs["validators"]
        )
        if column.nullable or prop.direction.name != "MANYTOONE":
            kwargs["allow_blank"] = True
            if not requirement_validator_specified:
                kwargs["validators"].append(validators.Optional())
        else:
            kwargs["allow_blank"] = False
            if not requirement_validator_specified:
                kwargs["validators"].append(validators.InputRequired())

        multiple = prop.direction.name in ("ONETOMANY", "MANYTOMANY") and prop.uselist
        return self._model_select_field(prop, multiple, remote_model, **kwargs)

    def convert(self, model, mapper, name, prop, field_args, hidden_pk):
        # Properly handle forced fields
        if isinstance(prop, FieldPlaceholder):
            unbound = prop.field
            return unbound.field_class(*unbound.args, **unbound.kwargs)

        kwargs = {"validators": [], "filters": []}

        if field_args:
            kwargs.update(field_args)

        if kwargs["validators"]:
            # Create a copy of the list since we will be modifying it.
            kwargs["validators"] = list(kwargs["validators"])

        # Check if it is relation or property
        if hasattr(prop, "direction"):
            return self._convert_relation(name, prop, kwargs)
        elif hasattr(prop, "columns"):
            column = prop.columns[0]
            form_columns = getattr(self.view, "form_columns", None) or ()

            # Do not display foreign keys - use relations, except when explicitly instructed
            if column.foreign_keys and prop.key not in form_columns:
                return None

            # Only display "real" columns
            if not isinstance(column, Column):
                return None

            unique = False

            if column.primary_key:
                if hidden_pk:
                    # If requested to add hidden field, show it
                    return HiddenField()
                else:
                    # By default, don't show primary keys either
                    # If PK is not explicitly allowed, ignore it
                    if prop.key not in form_columns:
                        return None

                    # Current Unique Validator does not work with multicolumns-pks
                    if not Query.has_multiple_pks(model):
                        kwargs["validators"].append(Unique(self.session, model, column))
                        unique = True

            # If field is unique, validate it
            if column.unique and not unique:
                kwargs["validators"].append(Unique(self.session, model, column))

            if (
                not column.nullable
                and not isinstance(column.type, (Boolean,))
                and not column.default
                and not column.server_default
            ):
                kwargs["validators"].append(validators.InputRequired())

            # Apply label and description if it isn't inline form field
            if self.view.model == mapper.class_:
                kwargs["label"] = self._get_label(prop.key, kwargs)
                kwargs["description"] = self._get_description(prop.key, kwargs)

            # Figure out default value
            default = getattr(column, "default", None)
            value = None

            if default is not None:
                value = getattr(default, "arg", None)

                if value is not None:
                    if getattr(default, "is_callable", False):
                        value = lambda: default.arg(None)  # noqa: E731
                    else:
                        if not getattr(default, "is_scalar", True):
                            value = None

            if value is not None:
                kwargs["default"] = value

            # Check nullable
            if column.nullable:
                kwargs["validators"].append(validators.Optional())

            # Check if a list of 'form_choices' are specified
            form_choices = getattr(self.view, "form_choices", None)
            if mapper.class_ == self.view.model and form_choices:
                choices = form_choices.get(prop.key)
                if choices:
                    return Select2Field(
                        choices=choices, allow_blank=column.nullable, **kwargs
                    )

            # Run converter
            converter = self.get_converter(column)

            if converter is None:
                return None

            return converter(
                model=model, mapper=mapper, prop=prop, column=column, field_args=kwargs
            )
        return None


# Get list of fields and generate form
def get_form(
    model,
    converter,
    base_class,
    only=None,
    exclude=None,
    field_args=None,
    hidden_pk=False,
    extra_fields=None,
):
    """
    Generate form from the model.

    :param model:
        Model to generate form from
    :param converter:
        Converter class to use
    :param base_class:
        Base form class
    :param only:
        Include fields
    :param exclude:
        Exclude fields
    :param field_args:
        Dictionary with additional field arguments
    :param hidden_pk:
        Generate hidden field with model primary key or not
    """

    field_args = field_args or {}
    
    mapper = inspect(model)

    if only:
        properties = []
        for name in only:
            if extra_fields and name in extra_fields:
                properties.append((name, FieldPlaceholder(extra_fields[name])))
            else:
                column, _path = Query.get_field_with_path(model, name)
                properties.append((column.key, column.property))
    else:
        properties = [(p.key, p) for p in mapper.attrs]
        if exclude:
            properties = [x for x in properties if x[0] not in exclude]

    field_dict = {}
    for name, p in properties:
        # Ignore protected properties
        if name.startswith("_"):
            continue

        field = converter.convert(
            model, mapper, name, p, field_args.get(name), hidden_pk
        )
        if field is not None:
            field_dict[name] = field

    # Contribute extra fields
    if not only and extra_fields:
        for name, field in extra_fields.items():
            unbound = field
            field_dict[name] = unbound.field_class(*unbound.args, **unbound.kwargs)

    return type(model.__name__ + "Form", (base_class,), field_dict)
