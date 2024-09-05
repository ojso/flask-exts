from werkzeug.datastructures import FileStorage
from wtforms import fields as wtforms_fields


class FileField(wtforms_fields.FileField):
    """Werkzeug-aware subclass of :class:`wtforms.fields.FileField`."""

    def process_formdata(self, valuelist):
        valuelist = (x for x in valuelist if isinstance(x, FileStorage) and x)
        data = next(valuelist, None)

        if data is not None:
            self.data = data
        else:
            self.raw_data = ()


class MultipleFileField(wtforms_fields.MultipleFileField):
    """Werkzeug-aware subclass of :class:`wtforms.fields.MultipleFileField`.
    """

    def process_formdata(self, valuelist):
        valuelist = (x for x in valuelist if isinstance(x, FileStorage) and x)
        data = list(valuelist) or None

        if data is not None:
            self.data = data
        else:
            self.raw_data = ()
