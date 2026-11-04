from sqlalchemy import inspect

from ....forms.fields.inline import InlineModelField
from ..form import get_model_form
from .inline_form import InlineForm


class InlineModelConverter:
    """Inline model form converter for collection and scalar relationships."""

    def __init__(self, session, view, model_converter):
        """Initialize the inline model converter.

        Args:
            session:
                SQLAlchemy session
            view:
                View object
            model_converter:
                Model converter class. Will be automatically instantiated with
                appropriate `InlineForm` instance.
        """

        self.view = view
        self.session = session
        self.model_converter = model_converter

    def get_label(self, info, name):
        """Get inline model field label

        Args:
            info:
                Inline model info
            name:
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
        """Figure out InlineForm information.

        Args:
            prop:
                Inline model. Can be one of:
                    - ``tuple``, first value is related model instance,second is options
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
        inline_form._ajax_refs = self.process_ajax_refs(inline_form)

        return inline_form

    def process_ajax_refs(self, inline_form):
        refs = getattr(inline_form, "ajax_refs", None)

        result = {}

        if refs:
            for name, opts in refs.items():
                new_name = f"{inline_form.model.__name__.lower()}-{name}"

                loader = None
                if isinstance(opts, dict):
                    loader = self.view.create_ajax_loader(
                        inline_form.model, self.session, new_name, name, opts
                    )
                else:
                    loader = opts
                    # If we're changing the name in self.view._ajax_refs, we
                    # must also change loader.name property. Otherwise when the
                    # widget tries to set the 'data-url' property in the <input>
                    # tag, it won't be able to find the loader since it'll be
                    # using the "field.loader.name" of the previously-configured
                    # loader.
                    loader.name = new_name

                result[name] = loader
                self.view._ajax_refs[new_name] = loader

        return result

    def _calculate_mapping_key_pair(self, model, info):
        """Calculate mapping property key pair between `model` and inline model,

            including the forward one for `model` and the reverse one for inline model.
            Override the method to map your own inline models.

        Args:
            model:
                Model class
            info:
                The InlineForm instance

        Returns:
            A dict of forward property key and reverse property key
        """
        mapper = inspect(model)

        # Find property from target model to current model
        # Use the base mapper to support inheritance
        target_mapper = inspect(info.model).base_mapper
        reverse_props = []
        forward_reverse_props_keys = {}
        for prop in target_mapper.iterate_properties:
            if (
                hasattr(prop, "direction")
                and prop.direction.name in ("MANYTOONE", "MANYTOMANY")
                and issubclass(model, prop.mapper.class_)
            ):
                # store props in reverse_props list
                reverse_props.append(prop)

        if not reverse_props:
            raise ValueError(f"Cannot find reverse relation for model {info.model}")

        for reverse_prop in reverse_props:
            if reverse_prop.direction.name == "MANYTOONE":
                candidate = "ONETOMANY"
            else:
                candidate = "MANYTOMANY"

            back_populates = getattr(reverse_prop, "back_populates", None)
            if back_populates:
                forward_prop = mapper.relationships.get(back_populates)
                if (
                    forward_prop is not None
                    and forward_prop.direction.name == candidate
                    and forward_prop.key not in forward_reverse_props_keys
                    and issubclass(target_mapper.class_, forward_prop.mapper.class_)
                ):
                    forward_reverse_props_keys[forward_prop.key] = reverse_prop.key
                    continue

            for prop in mapper.iterate_properties:
                if (
                    hasattr(prop, "direction")
                    and prop.direction.name == candidate
                    and prop.key not in forward_reverse_props_keys
                    and issubclass(target_mapper.class_, prop.mapper.class_)
                ):
                    forward_reverse_props_keys[prop.key] = reverse_prop.key
                    break
            else:
                raise ValueError(f"Cannot find forward relation for model {info.model}")

        return forward_reverse_props_keys

    def contribute(self, model, form_class, inline_model):
        """Generate form fields for inline model and contribute them to the `form_class`

        Args:
            model: Model class.
            form_class: Form to add properties to.
            inline_model: Inline model. Can be one of:
                - ``tuple``: first value is related model instance,
                  second is dictionary with options.
                - ``InlineForm`` instance.
                - Model class.

        Returns:
            Form class.
        """

        inline_form = self.get_inline_form(inline_model)

        forward_reverse_props_keys = self._calculate_mapping_key_pair(
            model, inline_form
        )

        for forward_prop_key, reverse_prop_key in forward_reverse_props_keys.items():
            # Remove reverse property from the list
            ignore = [reverse_prop_key]

            if inline_form.form_excluded_columns:
                exclude = ignore + list(inline_form.form_excluded_columns)
            else:
                exclude = ignore

            # Create converter
            converter = self.model_converter(self.session, inline_form)

            # Create form
            child_form = get_model_form(
                inline_form.model,
                converter,
                base_class=self.view.base_form_class,
                only=inline_form.form_columns,
                exclude=exclude,
                field_args=inline_form.form_args,
                extra_fields=inline_form.form_extra_fields,
            )

            kwargs = {}

            label = self.get_label(inline_form, forward_prop_key)
            if label:
                kwargs["label"] = label

            if self.view.form_args:
                field_args = self.view.form_args.get(forward_prop_key, {})
                kwargs.update(**field_args)

            relationship = inspect(model).relationships[forward_prop_key]
            inline_field = InlineModelField(
                child_form,
                inline_form.model,
                forward_prop_key,
                relationship.uselist,
                inline_form,
                **kwargs,
            )
            if not hasattr(self.view, "_inline_model_configs"):
                self.view._inline_model_configs = {}
            self.view._inline_model_configs[forward_prop_key] = {
                "form_class": child_form,
                "model": inline_form.model,
                "reverse_prop": reverse_prop_key,
                "is_collection": relationship.uselist,
            }
            # Contribute field
            setattr(
                form_class,
                forward_prop_key,
                inline_field,
            )

        return form_class
