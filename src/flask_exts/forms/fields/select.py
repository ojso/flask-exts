import re

import wtforms.fields

from ..widgets.select import SelectWidget, TagsWidget


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
        super().__init__(label, validators, coerce, choices, **kwargs)
        self.allow_blank = allow_blank
        self.blank_text = blank_text or " "

    def iter_choices(self):
        if self.allow_blank:
            yield ("", self.blank_text, self.data is None, {})

        for choice in self.choices:
            if isinstance(choice, tuple):
                yield (choice[0], choice[1], self.coerce(choice[0]) == self.data, {})
            else:
                yield (
                    choice.value,
                    choice.name,
                    self.coerce(choice.value) == self.data,
                    {},
                )

    def process_data(self, value):
        if value is None:
            self.data = None
        else:
            try:
                self.data = self.coerce(value)
            except (ValueError, TypeError):
                self.data = None

    def process_formdata(self, valuelist):
        if valuelist:
            if self.allow_blank and valuelist[0] == "":
                self.data = None
            else:
                try:
                    self.data = self.coerce(valuelist[0])
                except ValueError:
                    raise ValueError(self.gettext("Invalid Choice: could not coerce"))

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
