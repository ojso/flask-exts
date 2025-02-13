import json
from markupsafe import Markup
from flask import url_for
from wtforms.widgets import html_params
from wtforms.widgets import Select
from wtforms.widgets import TextInput


class Select2Widget(Select):
    """Select2 Widget."""

    def __call__(self, field, **kwargs):
        kwargs.setdefault("data-role", "select2")
        allow_blank = getattr(field, "allow_blank", False)
        if allow_blank and not self.multiple:
            kwargs["data-allow-blank"] = "1"

        return super().__call__(field, **kwargs)


class Select2TagsWidget(TextInput):
    """Select2Tags Widget."""

    def __call__(self, field, **kwargs):
        kwargs.setdefault("data-role", "select2-tags")
        kwargs.setdefault(
            "data-allow-duplicate-tags",
            "true" if getattr(field, "allow_duplicates", False) else "false",
        )
        return super().__call__(field, **kwargs)

class AjaxSelect2Widget:
    def __init__(self, multiple=False):
        self.multiple = multiple

    def __call__(self, field, **kwargs):
        kwargs.setdefault('data-role', 'select2-ajax')
        # todo
        kwargs.setdefault("data-url", url_for(".ajax_lookup", name=field.loader.name))
        # kwargs.setdefault('data-url', kwargs.pop("data_url", ""))

        allow_blank = getattr(field, 'allow_blank', False)
        if allow_blank and not self.multiple:
            kwargs['data-allow-blank'] = u'1'

        kwargs.setdefault('id', field.id)
        kwargs.setdefault('type', 'hidden')

        if self.multiple:
            result = []
            ids = []

            for value in field.data:
                data = field.loader.format(value)
                result.append(data)
                ids.append(str(data[0]))

            separator = getattr(field, 'separator', ',')

            kwargs['value'] = separator.join(ids)
            kwargs["data-json"] = json.dumps(result, default=str)
            kwargs['data-multiple'] = u'1'
            kwargs['data-separator'] = separator
        else:
            data = field.loader.format(field.data)

            if data:
                kwargs['value'] = data[0]
                kwargs['data-json'] = json.dumps(data, default=str)


        placeholder = field.loader.options.get('placeholder', field.gettext('Please select model'))
        kwargs.setdefault('data-placeholder', placeholder)

        minimum_input_length = int(field.loader.options.get('minimum_input_length', 1))
        kwargs.setdefault('data-minimum-input-length', minimum_input_length)

        kwargs.setdefault('data-separator', ',')

        return Markup('<select %s></select>' % html_params(name=field.name, **kwargs))

