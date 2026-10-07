from wtforms.widgets import TextInput


class DatePickerWidget(TextInput):
    """Date picker widget."""

    def __call__(self, field, **kwargs):
        kwargs.setdefault("data-role", "datepicker")
        kwargs.setdefault("data-date-format", "YYYY-MM-DD")

        self.date_format = kwargs["data-date-format"]
        return super().__call__(field, **kwargs)


class DateTimePickerWidget(TextInput):
    """Datetime picker widget."""

    def __call__(self, field, **kwargs):
        kwargs.setdefault("data-role", "datetimepicker")
        kwargs.setdefault("data-date-format", "YYYY-MM-DD HH:mm:ss")
        return super().__call__(field, **kwargs)


class TimePickerWidget(TextInput):
    """Date picker widget."""

    def __call__(self, field, **kwargs):
        kwargs.setdefault("data-role", "timepicker")
        kwargs.setdefault("data-date-format", "HH:mm:ss")
        return super().__call__(field, **kwargs)
