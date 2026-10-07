from markupsafe import Markup, escape
from wtforms.widgets import html_params


class CheckboxListInput:
    """
    Alternative widget for many-to-many relationships.

    Appears as the list of checkboxes.
    """

    def __call__(self, field, **kwargs):
        items = []

        for value, label, selected, _ in field.iter_choices():
            params = html_params(
                id=value,
                name=field.name,
                value=value,
                type="checkbox",
                checked=selected,
            )

            items.append(
                '<div class="checkbox"> <label>'
                f"<input {params}>{escape(label)} </label>"
                "</div>"
            )

        return Markup("".join(items))
