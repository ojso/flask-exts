import json

from markupsafe import Markup, escape
from wtforms.widgets import html_params


def _build_query_select_options(field):
    """返回 (data-options 的 JSON 字符串, 选中的 value 列表)。"""
    choices = []
    selected_ids = []
    for field_choices in field.iter_choices():
        if len(field_choices) == 3:
            value, label, selected = field_choices
        else:
            value, label, selected, _ = field_choices
        choices.append({"value": value, "label": label})
        if selected:
            selected_ids.append(value)
    return json.dumps(choices, default=str), selected_ids

class EditableWidget:
    """
    WTForms widget that provides in-line editing for the list view.

    Determines how to display the editable/ajax form based on the
    field inside of the FieldList (StringField, IntegerField, etc).
    """

    def __call__(self, field, **kwargs):
        display_value = kwargs.pop("display_value", "")
        kwargs.setdefault("class", "editable")
        kwargs.setdefault("data-value", display_value)
        kwargs.setdefault('data-url', './ajax/update/')
        # data_url = kwargs.pop("data_url", "")
        # kwargs.setdefault("data-url", data_url)
        kwargs.setdefault("data-name", field.name)
        kwargs.setdefault("href", "#")
        kwargs["data-pk"] = str(kwargs.pop("pk"))
        kwargs = self.get_kwargs(field, kwargs)

        return Markup(f"<a {html_params(**kwargs)}>{escape(display_value)}</a>")

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
            kwargs["data-type"] = "select"
            kwargs["data-value"] = "1" if field.data else ""
            kwargs["data-options"] = json.dumps(
                [
                    {"value": "", "text": field.gettext("No")},
                    {"value": "1", "text": field.gettext("Yes")},
                ]
            )
            kwargs["data-role"] = "x-editable-boolean"
        elif field.type in ["ChoiceField", "SelectField"]:
            kwargs["data-type"] = "select"
            choices = [{"value": x, "label": y} for x, y in field.choices]
            if getattr(field, "allow_blank", False):
                choices.insert(0, {"value": "", "label": ""})
            kwargs["data-options"] = json.dumps(choices)
        elif field.type == "DateField":
            kwargs["data-type"] = "combodate"
            kwargs["data-format"] = "YYYY-MM-DD"
            kwargs["data-template"] = "YYYY-MM-DD"
            kwargs["data-role"] = "x-editable-combodate"
        elif field.type == "DateTimeField":
            kwargs["data-type"] = "combodate"
            kwargs["data-format"] = "YYYY-MM-DD HH:mm:ss"
            kwargs["data-template"] = "YYYY-MM-DD  HH:mm:ss"
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
        ]:
            kwargs["data-type"] = "select"
            choices = []
            selected_ids = []
            for field_choices in field.iter_choices():
                if len(field_choices) == 3:
                    value, label, selected = field_choices
                else:
                    value, label, selected, _ = field_choices
                choices.append({"value": value, "label": label})
                if selected:
                    selected_ids.append(value)
            # blank field is already included if allow_blank
            kwargs["data-options"] = json.dumps(choices,default=str)

            if field.type == "QuerySelectMultipleField":
                kwargs["data-role"] = "x-editable-select-multiple"
                # must use id instead of text or prefilled values won't work
                separator = getattr(field, "separator", ",")
                kwargs["data-value"] = separator.join(selected_ids)
            else:
                kwargs["data-value"] = selected_ids[0]
        else:
            raise Exception(f"Unsupported field type: {type(field)}")

        return kwargs
