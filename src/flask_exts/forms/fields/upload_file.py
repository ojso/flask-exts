import os
import os.path as op
from werkzeug.utils import secure_filename
from werkzeug.datastructures import FileStorage
from wtforms import ValidationError
from wtforms.fields import FileField
from ...babel import _gettext


def is_uploaded_file(file_data):
    return file_data and isinstance(file_data, FileStorage) and file_data.filename


class UploadFileField(FileField):
    """
    Customizable file-upload field.

    Saves file to configured path, handles updates. Inherits from `FileField`,
    resulting filename will be stored as string.
    """

    def __init__(
        self,
        label=None,
        validators=None,
        base_path=None,
        allowed_extensions=None,
        allow_overwrite=False,
        **kwargs,
    ):
        """
        Constructor.

        :param label:
            Display label
        :param validators:
            Validators
        :param base_path:
            Absolute path to the directory which will store files
        :param allowed_extensions:
            List of allowed extensions. If not provided, will allow any file.
        :param allow_overwrite:
            Whether to overwrite existing files in upload directory. Defaults to `False`.
        """

        if not op.exists(base_path):
            raise ValueError("FileUploadField requires base_path to exist.")
        self.base_path = base_path
        self.allowed_extensions = allowed_extensions
        self.allow_overwrite = allow_overwrite
        super().__init__(label, validators, **kwargs)

    def is_file_allowed(self, filename):
        """Check if file extension is allowed.

        :param filename:
            File name to check
        """
        if not self.allowed_extensions:
            return True

        return "." in filename and filename.rsplit(".", 1)[1].lower() in map(
            lambda x: x.lower(), self.allowed_extensions
        )

    def pre_validate(self, form):
        if is_uploaded_file(self.data) and not self.is_file_allowed(self.data.filename):
            raise ValidationError(_gettext("Invalid file extension"))

    def save_file(self, filename=None):
        if filename is None:
            filename = secure_filename(self.data.filename)
        elif callable(filename):
            filename = filename(self.data)
        else:
            filename = secure_filename(filename)
        path = op.join(self.base_path, filename)
        if not self.allow_overwrite and os.path.exists(path):
            raise ValidationError(
                _gettext('File "%s" already exists.' % self.data.filename)
            )
        # update filename of FileStorage to our validated name
        self.data.filename = filename
        self.data.save(path)
        return filename
