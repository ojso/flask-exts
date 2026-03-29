import os
import os.path as op
from werkzeug.datastructures import FileStorage
from wtforms import ValidationError
from wtforms.fields import FileField as _FileField
from ..validators import FileAllowed
from ..widgets.file import ImageInput


def is_uploaded_file(file_data):
    return file_data and isinstance(file_data, FileStorage) and file_data.filename


def field_filename_generate(field,file_data: FileStorage):
    return file_data.filename.strip().replace(' ', '_')


class FileField(_FileField):
    """
    Customizable file-upload field.

    Saves file to configured path, handles updates. Inherits from `FileField`,
    resulting filename will be stored as string.
    """

    def __init__(
        self,
        label=None,
        validators=None,
        save_path=None,
        filename_generate=None,
        allow_overwrite=False,
        **kwargs,
    ):
        """
        Constructor.

        :param label:
            Display label
        :param validators:
            Validators
        :param save_path:
            Absolute path to the directory which will store files
        :param filename_generate:
            Function(File) that will generate filename from the model and uploaded file object.
        :param allow_overwrite:
            Whether to overwrite existing files in upload directory. Defaults to `False`.
        """

        self.save_path = save_path
        self.filename_generate = filename_generate or field_filename_generate
        self.allow_overwrite = allow_overwrite
        super().__init__(label, validators, **kwargs)

    def pre_validate(self, form):
        if (self.save_path is None) or (not op.exists(self.save_path)):
            raise ValidationError("FileField requires save_path to exist.")

        if is_uploaded_file(self.data):
            # check if not allow overwrite and file exist
            if not self.allow_overwrite:
                filename = self.filename_generate(self,self.data)
                path = op.join(self.save_path, filename)
                if os.path.exists(path):
                    raise ValidationError(
                        self.gettext('File "%s" already exists.' % self.data.filename)
                    )

    def save_file(self):
        if not is_uploaded_file(self.data):
            return None
        filename = self.filename_generate(self,self.data)
        path = op.join(self.save_path, filename)
        if not self.allow_overwrite and os.path.exists(path):
            raise FileExistsError(
                self.gettext('File "%s" already exists.' % self.data.filename)
            )
        # update filename of FileStorage to our validated name
        self.data.filename = filename
        self.data.save(path)
        return filename


class ImageField(FileField):
    """Image upload field.
    Does image validation
    """

    widget = ImageInput()

    def __init__(
        self,
        label=None,
        validators=None,
        save_path=None,
        filename_generate=None,
        allow_overwrite=False,
        **kwargs,
    ):

        if not validators:
            validators = [FileAllowed(["gif", "jpg", "jpeg", "png", "tiff"])]
        elif not any(isinstance(v,FileAllowed) for v in validators):
            validators.append(FileAllowed(["gif", "jpg", "jpeg", "png", "tiff"]))

        super().__init__(
            label,
            validators,
            save_path=save_path,
            filename_generate=filename_generate,
            allow_overwrite=allow_overwrite,
            **kwargs,
        )
