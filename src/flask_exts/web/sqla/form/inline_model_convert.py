from sqlalchemy import inspect
from ....forms.fields.sqla import InlineModelFormListField, InlineModelOneToOneField
from ..ajax import create_ajax_loader
from . import get_model_form
from .inline_form import InlineForm


class InlineModelConverter:
    """
    Inline model form converter.
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
            appropriate `InlineForm` instance.
        """

        self.view = view
        self.session = session
        self.model_converter = model_converter

    def get_label(self, info, name):
        """
        Get inline model field label

        :param info:
            Inline model info
        :param name:
            Field name
        """
        form_name = getattr(info, "form_label", None)
        if form_name:
            return form_name

        column_labels = getattr(self.view, "column_labels", None)

        if column_labels and name in column_labels:
            return column_labels[name]

        return None

    def get_inline_form(self, prop):
        """
        Figure out InlineForm information.

        :param p:
            Inline model. Can be one of:
                - ``tuple``, first value is related model instance,second is dictionary with options
                - ``InlineForm`` instance
                - Model class
        """
        if isinstance(prop, InlineForm):
            inline_form = prop
        elif isinstance(prop, tuple):
            inline_form = InlineForm(prop[0], **prop[1])
        else:
            inline_form = InlineForm(prop)

        # Resolve AJAX FKs
        inline_form._form_ajax_refs = self.process_ajax_refs(inline_form)

        return inline_form

    def process_ajax_refs(self, inline_form):
        refs = getattr(inline_form, "form_ajax_refs", None)

        result = {}

        if refs:
            for name, opts in refs.items():
                new_name = "%s-%s" % (inline_form.model.__name__.lower(), name)

                loader = None
                if isinstance(opts, dict):
                    loader = create_ajax_loader(
                        inline_form.model, self.session, new_name, name, opts
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
            The InlineForm instance
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
        Generate form fields for inline model and contribute them to the `form_class`

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
             - ``tuple``, first value is related model instance, second is dictionary with options
             - ``InlineForm`` instance
             - Model class

        :return:
            Form class
        """

        info = self.get_inline_form(inline_model)

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
            child_form = get_model_form(
                info.model,
                converter,
                base_class=info.base_form_class,
                only=info.form_columns,
                exclude=exclude,
                field_args=info.form_args,
                hidden_pk=True,
                extra_fields=info.form_extra_fields,
            )

            kwargs = dict()

            label = self.get_label(info, forward_prop_key)
            if label:
                kwargs["label"] = label

            if self.view.form_args:
                field_args = self.view.form_args.get(forward_prop_key, {})
                kwargs.update(**field_args)

            
            inline_field = InlineModelFormListField(
                child_form,
                self.session,
                info.model,
                reverse_prop_key,
                info,
                **kwargs,
            )
            # Contribute field
            setattr(
                form_class,
                forward_prop_key,
                inline_field,
            )

        return form_class


class InlineOneToOneModelConverter(InlineModelConverter):
    """
    Inline one-to-one model form converter.
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
        info = self.get_inline_form(inline_model)

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
        child_form = get_model_form(
            info.model,
            converter,
            base_class=info.base_form_class,
            only=info.form_columns,
            exclude=exclude,
            field_args=info.form_args,
            hidden_pk=True,
            extra_fields=info.form_extra_fields,
        )

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
