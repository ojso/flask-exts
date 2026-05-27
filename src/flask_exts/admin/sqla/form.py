from enum import Enum
from wtforms import validators
from sqlalchemy import inspect
from sqlalchemy import select
from sqlalchemy import Boolean, Column
from wtforms.fields import HiddenField
from wtforms.fields import StringField, TextAreaField, IntegerField, DecimalField,BooleanField
from wtforms.fields import DateField
# from wtforms.fields import TimeField
from ...template.forms.fields import TimeField
from wtforms.fields import DateTimeLocalField as DateTimeField
from ...template.forms.fields import Select2Field
from ...template.forms.fields import Select2TagsField
from ...template.forms.fields import JSONField
from ...template.forms.fields.ajax_select import AjaxSelectField
from ...template.forms.fields.ajax_select import AjaxSelectMultipleField
from ...template.forms.fields.sqla import QuerySelectField
from ...template.forms.fields.sqla import QuerySelectMultipleField
from ...template.forms.fields.sqla import InlineModelFormListField
from ...template.forms.fields.sqla import InlineModelOneToOneField
from ...template.forms.fields.inline import InlineFormField
from ...template.forms.widgets import DatePickerWidget
from ...template.forms.form.base_form import BaseForm
from ...template.forms.validators.sqla import Unique
from ..model.form import (
    ModelConverterBase,
    InlineModelConverterBase,
    FieldPlaceholder,
)

from .query import Query
from .ajax import create_ajax_loader


class AdminModelConverter(ModelConverterBase):
    """
    SQLAlchemy model to form converter
    """

    def _nullable_common(self, column, field_args, **extra):
        if column.nullable:
            filters = field_args.get("filters", [])
            filters.append(lambda x: x or None)
            field_args["filters"] = filters

    def _string_common(self, column, field_args, **extra):
        if (
            hasattr(column.type, "length")
            and isinstance(column.type.length, int)
            and column.type.length
        ):
            field_args["validators"].append(validators.Length(max=column.type.length))
        self._nullable_common(column, field_args, **extra)

    def conv_string(self, column, field_args, **extra):
        self._string_common(column=column, field_args=field_args, **extra)
        return StringField(**field_args)

    def conv_text(self, field_args, **extra):
        self._string_common(field_args=field_args, **extra)
        return TextAreaField(**field_args)

    def conv_boolean(self, field_args, **extra):
        return BooleanField(**field_args)

    def convert_integer(self, column, field_args, **extra):
        unsigned = getattr(column.type, "unsigned", False)
        if unsigned:
            field_args["validators"].append(validators.NumberRange(min=0))
        return IntegerField(**field_args)

    def convert_decimal(self, column, field_args, **extra):
        # override default decimal places limit, use database defaults instead
        field_args.setdefault("places", None)
        return DecimalField(**field_args)

    def convert_date(self, field_args, **extra):
        field_args["widget"] = DatePickerWidget()
        return DateField(**field_args)

    def convert_time(self, field_args, **extra):
        return TimeField(**field_args)

    def convert_datetime(self, field_args, **extra):
        return DateTimeField(**field_args)

    def convert_enum(self, column, field_args, **extra):
        available_choices = [(f, f) for f in column.type.enums]
        accepted_values = [choice[0] for choice in available_choices]

        if column.nullable:
            field_args["allow_blank"] = column.nullable
            accepted_values.append(None)

        self._nullable_common(column, field_args)

        field_args["choices"] = available_choices
        field_args["validators"].append(validators.AnyOf(accepted_values))
        field_args["coerce"] = lambda v: v.name if isinstance(v, Enum) else str(v)
        return Select2Field(**field_args)

    def convert_json(self, field_args, **extra):
        return JSONField(**field_args)

    TYPE_MAPPING = {
        "conv_string": ["String"],
        "conv_text": ["Text"],
        "conv_boolean": ["Boolean"],
        "conv_integer": ["Integer", "BigInteger", "SmallInteger"],
        "conv_decimal": ["Numeric", "DECIMAL", "Float", "REAL", "DOUBLE"],
        "conv_date": ["Date"],
        "conv_time": ["Time"],
        "conv_datetime": ["DateTime"],
        "conv_enum": ["sqlalchemy.sql.sqltypes.Enum"],
        "conv_json": ["JSON"],
    }

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
    base_class=BaseForm,
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
    mapper = inspect(model)
    field_args = field_args or {}

    properties = [(p.key, p) for p in mapper.attrs]

    if only:

        def find(name):
            # If field is in extra_fields, it has higher priority
            if extra_fields and name in extra_fields:
                return name, FieldPlaceholder(extra_fields[name])
            column, path = Query.get_field_with_path(model, name)
            relation_name = column.key

            if column is not None and hasattr(column, "property"):
                return relation_name, column.property

            raise ValueError("Invalid model property name %s.%s" % (model, name))

        # Filter properties while maintaining property order in 'only' list
        properties = [find(x) for x in only]
    elif exclude:
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


class InlineModelConverter(InlineModelConverterBase):
    """
    Inline model form helper.
    """

    inline_field_list_type = InlineModelFormListField
    """
        Used field list type.

        If you want to do some custom rendering of inline field lists,
        you can create your own wtforms field and use it instead
    """

    def __init__(self, session, view, model_converter):
        """
        Constructor.

        :param session:
            SQLAlchemy session
        :param view:
            View object
        :param model_converter:
            Model converter class. Will be automatically instantiated with
            appropriate `InlineFormAdmin` instance.
        """
        super().__init__(view)
        self.session = session
        self.model_converter = model_converter

    def get_info(self, p):
        info = super().get_info(p)

        # Special case for model instances
        if info is None:
            if hasattr(p, "_sa_class_manager"):
                return self.form_admin_class(p)
            else:
                model = getattr(p, "model", None)

                if model is None:
                    raise Exception("Unknown inline model admin: %s" % repr(p))

                attrs = dict()
                for attr in dir(p):
                    if not attr.startswith("_") and attr != "model":
                        attrs[attr] = getattr(p, attr)

                return self.form_admin_class(model, **attrs)

            info = self.form_admin_class(model, **attrs)

        # Resolve AJAX FKs
        info._form_ajax_refs = self.process_ajax_refs(info)

        return info

    def process_ajax_refs(self, info):
        refs = getattr(info, "form_ajax_refs", None)

        result = {}

        if refs:
            for name, opts in refs.items():
                new_name = "%s-%s" % (info.model.__name__.lower(), name)

                loader = None
                if isinstance(opts, dict):
                    loader = create_ajax_loader(
                        info.model, self.session, new_name, name, opts
                    )
                else:
                    loader = opts
                    # If we're changing the name in self.view._form_ajax_refs,
                    # we must also change loader.name property. Otherwise
                    # when the widget tries to set the 'data-url' property in the <input> tag,
                    # it won't be able to find the loader since it'll be using the "field.loader.name"
                    # of the previously-configured loader.
                    setattr(loader, "name", new_name)

                result[name] = loader
                self.view._form_ajax_refs[new_name] = loader

        return result

    def _calculate_mapping_key_pair(self, model, info):
        """
        Calculate mapping property key pair between `model` and inline model,
            including the forward one for `model` and the reverse one for inline model.
            Override the method to map your own inline models.

        :param model:
            Model class
        :param info:
            The InlineFormAdmin instance
        :return:
            A dict of forward property key and reverse property key
        """
        mapper = inspect(model)

        # Find property from target model to current model
        # Use the base mapper to support inheritance
        target_mapper = inspect(info.model).base_mapper
        reverse_props = []
        forward_reverse_props_keys = dict()
        for prop in target_mapper.iterate_properties:
            if hasattr(prop, "direction") and prop.direction.name in (
                "MANYTOONE",
                "MANYTOMANY",
            ):
                if issubclass(model, prop.mapper.class_):
                    # store props in reverse_props list
                    reverse_props.append(prop)

        if not reverse_props:
            raise Exception("Cannot find reverse relation for model %s" % info.model)

        for reverse_prop in reverse_props:
            # Find forward property

            if reverse_prop.direction.name == "MANYTOONE":
                candidate = "ONETOMANY"
            else:
                candidate = "MANYTOMANY"

            for prop in mapper.iterate_properties:
                if hasattr(prop, "direction") and prop.direction.name == candidate:
                    # check if prop is not handled yet
                    # issubclass is more useful than equal comparator in the case of inheritance
                    if prop.key not in forward_reverse_props_keys.keys() and issubclass(
                        target_mapper.class_, prop.mapper.class_
                    ):
                        forward_reverse_props_keys[prop.key] = reverse_prop.key
                        break
            else:
                raise Exception(
                    "Cannot find forward relation for model %s" % info.model
                )

        return forward_reverse_props_keys

    def contribute(self, model, form_class, inline_model):
        """
        Generate form fields for inline forms and contribute them to
        the `form_class`

        :param converter:
            ModelConverterBase instance
        :param session:
            SQLAlchemy session
        :param model:
            Model class
        :param form_class:
            Form to add properties to
        :param inline_model:
            Inline model. Can be one of:

             - ``tuple``, first value is related model instance,
             second is dictionary with options
             - ``InlineFormAdmin`` instance
             - Model class

        :return:
            Form class
        """

        info = self.get_info(inline_model)

        forward_reverse_props_keys = self._calculate_mapping_key_pair(model, info)

        for forward_prop_key, reverse_prop_key in forward_reverse_props_keys.items():
            # Remove reverse property from the list
            ignore = [reverse_prop_key]

            if info.form_excluded_columns:
                exclude = ignore + list(info.form_excluded_columns)
            else:
                exclude = ignore

            # Create converter
            converter = self.model_converter(self.session, info)

            # Create form
            child_form = info.get_form()

            if child_form is None:
                child_form = get_form(
                    info.model,
                    converter,
                    base_class=info.form_base_class or BaseForm,
                    only=info.form_columns,
                    exclude=exclude,
                    field_args=info.form_args,
                    hidden_pk=True,
                    extra_fields=info.form_extra_fields,
                )

            # Post-process form
            child_form = info.postprocess_form(child_form)

            kwargs = dict()

            label = self.get_label(info, forward_prop_key)
            if label:
                kwargs["label"] = label

            if self.view.form_args:
                field_args = self.view.form_args.get(forward_prop_key, {})
                kwargs.update(**field_args)

            # Contribute field
            setattr(
                form_class,
                forward_prop_key,
                self.inline_field_list_type(
                    child_form,
                    self.session,
                    info.model,
                    reverse_prop_key,
                    info,
                    **kwargs,
                ),
            )

        return form_class


class InlineOneToOneModelConverter(InlineModelConverter):
    inline_field_list_type = InlineModelOneToOneField

    def _calculate_mapping_key_pair(self, model, info):

        mapper = inspect(info.model).base_mapper
        target_mapper = inspect(info.model)

        inline_relationship = dict()

        for forward_prop in mapper.iterate_properties:
            if not hasattr(forward_prop, "direction"):
                continue

            if forward_prop.direction.name != "MANYTOONE":
                continue

            if forward_prop.mapper.class_ != target_mapper.class_:
                continue

            # in case when model has few relationships to target model or
            # has just installed references manually. This is more quick
            # solution rather than rotate yet another one loop
            ref = getattr(forward_prop, "backref")

            if not ref:
                ref = getattr(forward_prop, "back_populates")

            if ref:
                inline_relationship[ref] = forward_prop.key
                continue

            # here we suppose that model has only one relationship
            # to target model and prop has not any reference
            for backward_prop in target_mapper.iterate_properties:
                if not hasattr(backward_prop, "direction"):
                    continue

                if backward_prop.direction.name != "ONETOMANY":
                    continue

                if issubclass(model, backward_prop.mapper.class_):
                    inline_relationship[backward_prop.key] = forward_prop.key
                    break
            else:
                raise Exception(
                    "Cannot find reverse relation for model %s" % info.model
                )
            break

        if not inline_relationship:
            raise Exception("Cannot find forward relation for model %s" % info.model)

        return inline_relationship

    def contribute(self, model, form_class, inline_model):
        info = self.get_info(inline_model)

        inline_relationships = self._calculate_mapping_key_pair(model, info)

        # Remove reverse property from the list
        ignore = [value for value in inline_relationships.values()]

        if info.form_excluded_columns:
            exclude = ignore + list(info.form_excluded_columns)
        else:
            exclude = ignore

        # Create converter
        converter = self.model_converter(self.session, info)

        # Create form
        child_form = info.get_form()

        if child_form is None:
            child_form = get_form(
                info.model,
                converter,
                base_class=info.form_base_class or BaseForm,
                only=info.form_columns,
                exclude=exclude,
                field_args=info.form_args,
                hidden_pk=True,
                extra_fields=info.form_extra_fields,
            )

        # Post-process form
        child_form = info.postprocess_form(child_form)

        kwargs = dict()

        # Contribute field
        for key in inline_relationships.keys():
            setattr(
                form_class,
                key,
                self.inline_field_list_type(
                    child_form,
                    self.session,
                    info.model,
                    inline_relationships[key],
                    info,
                    **kwargs,
                ),
            )

        return form_class
