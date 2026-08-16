"""
内联模型表单处理

提取 InlineModelConverter 和 InlineOneToOneModelConverter
以及相关的表单生成逻辑。

这个模块专门处理内联关系模型的表单转换，使 form.py 更轻量化。
"""

from sqlalchemy import inspect
from ...forms.fields.sqla import InlineModelFormListField, InlineModelOneToOneField
from ...forms.form.base_form import BaseForm
from ..model.form import InlineModelConverterBase
from .query import Query
from .ajax import create_ajax_loader
from .form import get_form


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
    """
    Inline one-to-one model form helper.

    用于处理一对一关系的内联表单转换。
    """
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
