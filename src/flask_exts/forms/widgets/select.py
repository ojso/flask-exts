import json

from flask import url_for
from markupsafe import Markup
from wtforms.widgets import Select, TextInput, html_params


class SelectWidget(Select):
    """Native HTML select widget."""

    def __init__(self, multiple=False):
        super().__init__(multiple=multiple)


class TomSelectWidget(SelectWidget):
    """Opt-in enhanced select widget powered by Tom Select."""

    def __call__(self, field, **kwargs):
        kwargs.setdefault("data-role", "tom-select")
        kwargs.setdefault("data-tom-select", "1")
        return super().__call__(field, **kwargs)


class TagsWidget(TextInput):
    """Native text input for comma-separated tags."""


class AjaxSelectWidget:
    """Select widget for remote choices, enhanced with Tom Select."""

    input_type = "tom-select-ajax"

    def __init__(self, multiple=False):
        self.multiple = multiple

    def __call__(self, field, **kwargs):
        kwargs.setdefault("data-role", "tom-select-ajax")
        kwargs.setdefault("data-tom-select", "ajax")
        kwargs.setdefault("data-url", url_for(".ajax_lookup", name=field.loader.name))
        allow_blank = getattr(field, "allow_blank", False)
        if allow_blank and not self.multiple:
            kwargs["data-allow-blank"] = "1"

        kwargs.setdefault("id", field.id)
        if self.multiple:
            values = []
            selected_ids = []
            for value in field.data:
                item = field.loader.format(value)
                values.append(item)
                selected_ids.append(str(item[0]))
            separator = getattr(field, "separator", ",")
            kwargs["value"] = separator.join(selected_ids)
            kwargs["data-json"] = json.dumps(values, default=str)
            kwargs["data-multiple"] = "1"
            kwargs["data-separator"] = separator
        else:
            item = field.loader.format(field.data)
            if item:
                kwargs["value"] = item[0]
                kwargs["data-json"] = json.dumps(item, default=str)

        placeholder = field.loader.options.get(
            "placeholder", field.gettext("Please select model")
        )
        kwargs.setdefault("data-placeholder", placeholder)
        kwargs.setdefault(
            "data-minimum-input-length",
            int(field.loader.options.get("minimum_input_length", 1)),
        )
        kwargs.setdefault("data-separator", ",")

        return Markup(
            f'<select {html_params(name=field.name, multiple=self.multiple, **kwargs)}></select>'
        )
