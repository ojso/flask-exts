import re
import wtforms.fields
from ..widgets.select import Select2Widget, Select2TagsWidget


class Select2Field(wtforms.fields.SelectField):
    """
    `Select2 <https://github.com/ivaynberg/select2>`_ styled select widget.

    You must include select2.js, form-x.x.x.js and select2 stylesheet for it to
    work.
    """

    widget = Select2Widget()

    def __init__(
        self,
        label=None,
        validators=None,
        coerce=str,
        choices=None,
        allow_blank=False,
        blank_text=None,
        **kwargs
    ):
        super().__init__(label, validators, coerce, choices, **kwargs)
        self.allow_blank = allow_blank
        self.blank_text = blank_text or " "

    def iter_choices(self):
        if self.allow_blank:
            yield ("__None", self.blank_text, self.data is None,{})

        for choice in self.choices:
            if isinstance(choice, tuple):
                yield (choice[0], choice[1], self.coerce(choice[0]) == self.data,{})
            else:
                yield (
                    choice.value,
                    choice.name,
                    self.coerce(choice.value) == self.data,
                    {}
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
            if valuelist[0] == "__None":
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


class Select2TagsField(wtforms.fields.StringField):
    """`Select2 <http://ivaynberg.github.com/select2/#tags>`_ styled text field.
    You must include select2.js, form-x.x.x.js and select2 stylesheet for it to work.
    """

    widget = Select2TagsWidget()
    _strip_regex = re.compile(
        r"#\d+(?:(,)|\s$)"
    )  # e.g., 'tag#123, anothertag#425 ' => 'tag, anothertag'

    def __init__(
        self,
        label=None,
        validators=None,
        save_as_list=False,
        coerce=str,
        allow_duplicates=False,
        **kwargs
    ):
        """Initialization

        :param save_as_list:
            If `True` then populate ``obj`` using list else string
        :param allow_duplicates
            If `True` then duplicate tags are allowed in the field.
        """
        self.save_as_list = save_as_list
        self.allow_duplicates = allow_duplicates
        self.coerce = coerce

        super().__init__(label, validators, **kwargs)

    def process_formdata(self, valuelist):
        if valuelist:
            entrylist = valuelist[0]
            if self.allow_duplicates and entrylist.endswith(" "):
                # This means this is an allowed duplicate (see form.js, `createSearchChoice`), so its ID was modified.
                # Hence, we need to restore the original IDs.
                entrylist = re.sub(self._strip_regex, "\\1", entrylist)
            if self.save_as_list:
                self.data = [
                    self.coerce(v.strip()) for v in entrylist.split(",") if v.strip()
                ]
            else:
                self.data = self.coerce(entrylist)

    def _value(self):
        if isinstance(self.data, (list, tuple)):
            return ",".join(v for v in self.data)
        elif self.data:
            return self.data
        else:
            return ""
