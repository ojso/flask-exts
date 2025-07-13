import json
from markupsafe import escape, Markup
from wtforms.widgets import html_params


class XEditableWidget:
    """
    WTForms widget that provides in-line editing for the list view.

    Determines how to display the x-editable/ajax form based on the
    field inside of the FieldList (StringField, IntegerField, etc).
    """

    def __call__(self, field, **kwargs):
        display_value = kwargs.pop("display_value", "")
        kwargs.setdefault("data-value", display_value)
        # todo
        kwargs.setdefault('data-url', './ajax/update/')
        # data_url = kwargs.pop("data_url", "")
        # kwargs.setdefault("data-url", data_url)

        kwargs.setdefault("data-role", "x-editable")

        kwargs.setdefault("id", field.id)
        kwargs.setdefault("name", field.name)
        kwargs.setdefault("href", "#")

        if not kwargs.get("pk"):
            raise Exception("pk required")
        kwargs["data-pk"] = str(kwargs.pop("pk"))

        kwargs["data-csrf"] = kwargs.pop("csrf", "")
        kwargs = self.get_kwargs(field, kwargs)

        return Markup("<a %s>%s</a>" % (html_params(**kwargs), escape(display_value)))

    def get_kwargs(self, field, kwargs):
        """
        Return extra kwargs based on the field type.
        """
        if field.type == "StringField":
            kwargs["data-type"] = "text"
        elif field.type == "TextAreaField":
            kwargs["data-type"] = "textarea"
            kwargs["data-rows"] = "5"
        elif field.type == "BooleanField":
            kwargs["data-type"] = "select2"
            kwargs["data-value"] = "1" if field.data else ""
            # data-source = dropdown options
            kwargs["data-source"] = json.dumps(
                [
                    {"value": "", "text": field.gettext("No")},
                    {"value": "1", "text": field.gettext("Yes")},
                ]
            )
            kwargs["data-role"] = "x-editable-boolean"
        elif field.type in ["Select2Field", "SelectField"]:
            kwargs["data-type"] = "select2"
            choices = [{"value": x, "text": y} for x, y in field.choices]

            # prepend a blank field to choices if allow_blank = True
            if getattr(field, "allow_blank", False):
                choices.insert(0, {"value": "__None", "text": ""})

            # json.dumps fixes issue with unicode strings not loading correctly
            kwargs["data-source"] = json.dumps(choices)
        elif field.type == "DateField":
            kwargs["data-type"] = "combodate"
            kwargs["data-format"] = "YYYY-MM-DD"
            kwargs["data-template"] = "YYYY-MM-DD"
            kwargs["data-role"] = "x-editable-combodate"
        elif field.type == "DateTimeField":
            kwargs["data-type"] = "combodate"
            kwargs["data-format"] = "YYYY-MM-DD HH:mm:ss"
            kwargs["data-template"] = "YYYY-MM-DD  HH:mm:ss"
            # x-editable-combodate uses 1 minute increments
            kwargs["data-role"] = "x-editable-combodate"
        elif field.type == "TimeField":
            kwargs["data-type"] = "combodate"
            kwargs["data-format"] = "HH:mm:ss"
            kwargs["data-template"] = "HH:mm:ss"
            kwargs["data-role"] = "x-editable-combodate"
        elif field.type == "IntegerField":
            kwargs["data-type"] = "number"
        elif field.type in ["FloatField", "DecimalField"]:
            kwargs["data-type"] = "number"
            kwargs["data-step"] = "any"
        elif field.type in [
            "QuerySelectField",
            "ModelSelectField",
            "QuerySelectMultipleField",
            "KeyPropertyField",
        ]:
            # QuerySelectField and ModelSelectField are for relations
            kwargs["data-type"] = "select2"

            choices = []
            selected_ids = []
            for field_choices in field.iter_choices():
                if len(field_choices) == 3:  # wtforms <3.1, >=3.1.1, <3.2
                    value, label, selected = field_choices
                else:
                    value, label, selected, _ = field_choices
                choices.append({"value": value, "text": label})
                if selected:
                    selected_ids.append(value)

            # blank field is already included if allow_blank
            kwargs["data-source"] = json.dumps(choices,default=str)

            if field.type == "QuerySelectMultipleField":
                kwargs["data-role"] = "x-editable-select2-multiple"

                # must use id instead of text or prefilled values won't work
                separator = getattr(field, "separator", ",")
                kwargs["data-value"] = separator.join(selected_ids)
            else:
                kwargs["data-value"] = selected_ids[0]
        else:
            raise Exception("Unsupported field type: %s" % (type(field),))

        return kwargs
