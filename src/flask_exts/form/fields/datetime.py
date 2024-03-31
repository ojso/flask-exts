import time
import datetime
from wtforms import fields as wtforms_fields
from ..widgets.datetime import DateTimePickerWidget
from ..widgets.datetime import TimePickerWidget
from ..babel import gettext


class DateTimeField(wtforms_fields.DateTimeField):
    """
    Allows modifying the datetime format of a DateTimeField using form_args.
    """

    widget = DateTimePickerWidget()

    def __init__(self, label=None, validators=None, format=None, **kwargs):
        """Constructor

        :param label:
            Label
        :param validators:
            Field validators
        :param format:
            Format for text to date conversion. Defaults to '%Y-%m-%d %H:%M:%S'
        :param kwargs:
            Any additional parameters
        """
        super().__init__(
            label, validators, format or "%Y-%m-%d %H:%M:%S", **kwargs
        )


class TimeField(wtforms_fields.Field):
    """
    A text field which stores a `datetime.time` object.
    Accepts time string in multiple formats: 20:10, 20:10:00, 10:00 am, 9:30pm, etc.
    """

    widget = TimePickerWidget()

    def __init__(
        self,
        label=None,
        validators=None,
        formats=None,
        default_format=None,
        widget_format=None,
        **kwargs
    ):
        """
        Constructor

        :param label:
            Label
        :param validators:
            Field validators
        :param formats:
            Supported time formats, as a enumerable.
        :param default_format:
            Default time format. Defaults to '%H:%M:%S'
        :param kwargs:
            Any additional parameters
        """
        super(TimeField, self).__init__(label, validators, **kwargs)

        self.formats = formats or (
            "%H:%M:%S",
            "%H:%M",
            "%I:%M:%S%p",
            "%I:%M%p",
            "%I:%M:%S %p",
            "%I:%M %p",
        )

        self.default_format = default_format or "%H:%M:%S"

    def _value(self):
        if self.raw_data:
            return " ".join(self.raw_data)
        elif self.data is not None:
            return self.data.strftime(self.default_format)
        else:
            return ""

    def process_formdata(self, valuelist):
        if valuelist:
            date_str = " ".join(valuelist)

            if date_str.strip():
                for format in self.formats:
                    try:
                        timetuple = time.strptime(date_str, format)
                        self.data = datetime.time(
                            timetuple.tm_hour, timetuple.tm_min, timetuple.tm_sec
                        )
                        return
                    except ValueError:
                        pass

                raise ValueError(gettext("Invalid time format"))
            else:
                self.data = None
