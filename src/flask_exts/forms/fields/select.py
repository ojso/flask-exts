import re

import wtforms.fields
from wtforms.fields import Choice, SelectChoice

from ..widgets.select import SelectWidget, TagsWidget


def _to_select_choice(choice, optgroup=None):
    if isinstance(choice, Choice):
        return SelectChoice(
            value=choice.value,
            label=choice.label,
            render_kw=choice.render_kw,
            optgroup=optgroup,
        )
    return SelectChoice.from_input(choice, optgroup)


def normalize_choices(choices):
    """Normalize legacy choice inputs to ``SelectChoice`` instances.

    ``SelectChoice`` is the supported input type for ``choices=...``. Plain
    strings, 2- or 3-item tuples, and the legacy dict forms are accepted for
    compatibility and converted here so WTForms does not emit its
    deprecation warnings.
    """
    if choices is None or callable(choices):
        return choices
    if isinstance(choices, dict):
        normalized = []
        for key, value in choices.items():
            if isinstance(value, dict):
                for inner_value, inner_label in value.items():
                    normalized.append(
                        SelectChoice(
                            value=inner_value,
                            label=inner_label,
                            optgroup=key,
                        )
                    )
            elif isinstance(value, (list, tuple)):
                normalized.extend(
                    _to_select_choice(item, optgroup=key) for item in value
                )
            else:
                normalized.append(SelectChoice(value=key, label=value))
        return normalized
    return [_to_select_choice(choice) for choice in choices]


class ChoiceField(wtforms.fields.SelectField):
    """Select field rendered as a native HTML select by default."""

    widget = SelectWidget()

    def __init__(
        self,
        label=None,
        validators=None,
        coerce=str,
        choices=None,
        allow_blank=False,
        blank_text=None,
        **kwargs,
    ):
        super().__init__(
            label=label,
            validators=validators,
            coerce=coerce,
            choices=normalize_choices(choices),
            **kwargs,
        )
        self.allow_blank = allow_blank
        self.blank_text = blank_text or " "

    def iter_choices(self):
        if self.allow_blank:
            yield Choice("", self.blank_text, self.data is None, {})
        yield from super().iter_choices()

    def iter_groups(self):
        if self.allow_blank:
            yield None, [Choice("", self.blank_text, self.data is None, {})]
        yield from super().iter_groups()

    def process_data(self, value):
        if value is None:
            self.data = None
        else:
            try:
                self.data = self.coerce(value)
            except (ValueError, TypeError):
                self.data = None

    def process_formdata(self, valuelist):
        if not valuelist:
            return
        if self.allow_blank and valuelist[0] == "":
            self.data = None
            return
        try:
            self.data = self.coerce(valuelist[0])
        except (ValueError, TypeError) as exc:
            raise ValueError(
                self.invalid_value_message
                or self.gettext("Invalid Choice: could not coerce.")
            ) from exc

    def pre_validate(self, form):
        if self.allow_blank and self.data is None:
            return

        super().pre_validate(form)


class TagsField(wtforms.fields.StringField):
    """Text field for comma-separated tags, optionally storing a list."""

    widget = TagsWidget()
    _strip_regex = re.compile(r"#\d+(?:(,)|\s$)")

    def __init__(
        self,
        label=None,
        validators=None,
        save_as_list=False,
        coerce=str,
        allow_duplicates=False,
        **kwargs,
    ):
        self.save_as_list = save_as_list
        self.allow_duplicates = allow_duplicates
        self.coerce = coerce
        super().__init__(label, validators, **kwargs)

    def process_formdata(self, valuelist):
        if valuelist:
            entrylist = valuelist[0]
            if self.allow_duplicates and entrylist.endswith(" "):
                entrylist = re.sub(self._strip_regex, "\\1", entrylist)
            if self.save_as_list:
                self.data = [
                    self.coerce(value.strip())
                    for value in entrylist.split(",")
                    if value.strip()
                ]
            else:
                self.data = self.coerce(entrylist)

    def _value(self):
        if isinstance(self.data, (list, tuple)):
            return ",".join(str(value) for value in self.data)
        if self.data:
            return self.data
        return ""
