from collections import abc
from wtforms.validators import DataRequired
from wtforms.validators import StopValidation
from wtforms.validators import ValidationError
from werkzeug.datastructures import FileStorage

class FileRequired(DataRequired):
    """Validates that the uploaded files(s) is a Werkzeug
    :class:`~werkzeug.datastructures.FileStorage` object.
    """

    def __call__(self, form, field):
        field_data = [field.data] if not isinstance(field.data, list) else field.data
        if not (
            all(isinstance(x, FileStorage) and x for x in field_data) and field_data
        ):
            raise StopValidation(
                self.message or field.gettext("This field is required.")
            )


class FileAllowed:
    """Validates the uploaded file(s) is allowed by a given list of extensions.

    :param upload_set: A list of extensions
    :param message: error message
    """

    def __init__(self, upload_set, message=None):
        self.upload_set = upload_set
        self.message = message

    def __call__(self, form, field):
        field_data = [field.data] if not isinstance(field.data, list) else field.data
        if not (
            all(isinstance(x, FileStorage) and x for x in field_data) and field_data
        ):
            return

        filenames = [f.filename.lower() for f in field_data]

        for filename in filenames:
            if isinstance(self.upload_set, abc.Iterable):
                if any(filename.endswith("." + x) for x in self.upload_set):
                    continue

                raise StopValidation(
                    self.message
                    or field.gettext(
                        "File does not have an approved extension: {extensions}"
                    ).format(extensions=", ".join(self.upload_set))
                )

class FileSize:
    """Validates that the uploaded file(s) is within a minimum and maximum
    file size (set in bytes).

    :param min_size: minimum allowed file size (in bytes). Defaults to 0 bytes.
    :param max_size: maximum allowed file size (in bytes).
    :param message: error message

    """

    def __init__(self, max_size, min_size=0, message=None):
        self.min_size = min_size
        self.max_size = max_size
        self.message = message

    def __call__(self, form, field):
        field_data = [field.data] if not isinstance(field.data, list) else field.data
        if not (
            all(isinstance(x, FileStorage) and x for x in field_data) and field_data
        ):
            return

        for f in field_data:
            file_size = len(f.read())
            f.seek(0)  # reset cursor position to beginning of file

            if (file_size < self.min_size) or (file_size > self.max_size):
                # the file is too small or too big => validation failure
                raise ValidationError(
                    self.message
                    or field.gettext(
                        "File must be between {min_size} and {max_size} bytes.".format(
                            min_size=self.min_size, max_size=self.max_size
                        )
                    )
                )


