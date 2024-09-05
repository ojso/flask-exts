import os
import os.path as op
from PIL import Image, ImageOps
from wtforms import ValidationError
from ..widgets.upload import ImageUploadInput
from .upload_file import FileUploadField


def thumbgen_filename(filename):
    """
    Generate thumbnail name from filename.
    """
    name, ext = op.splitext(filename)
    return "%s_thumb%s" % (name, ext)


class UploadImageField(FileUploadField):
    """
    Image upload field.

    Does image validation, thumbnail generation, updating and deleting images.

    Requires PIL (or Pillow) to be installed.
    """

    widget = ImageUploadInput()

    keep_image_formats = ("PNG",)
    """
        If field detects that uploaded image is not in this list, it will save image
        as PNG.
    """

    def __init__(
        self,
        label=None,
        validators=None,
        base_path=None,
        relative_path=None,
        namegen=None,
        allowed_extensions=None,
        max_size=None,
        thumbgen=None,
        thumbnail_size=None,
        permission=0o666,
        url_relative_path=None,
        endpoint="static",
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
        :param relative_path:
            Relative path from the directory. Will be prepended to the file name for uploaded files.
            Flask uses `urlparse.urljoin` to generate resulting filename, so make sure you have
            trailing slash.
        :param namegen:
            Function that will generate filename from the model and uploaded file object.
            Please note, that model is "dirty" model object, before it was committed to database.

            For example::

                import os.path as op

                def prefix_name(obj, file_data):
                    parts = op.splitext(file_data.filename)
                    return secure_filename('file-%s%s' % parts)

                class MyForm(BaseForm):
                    upload = FileUploadField('File', namegen=prefix_name)

        :param allowed_extensions:
            List of allowed extensions. If not provided, then gif, jpg, jpeg, png and tiff will be allowed.
        :param max_size:
            Tuple of (width, height, force) or None. If provided, Flask-Admin will
            resize image to the desired size.

            Width and height is in pixels. If `force` is set to `True`, will try to fit image into dimensions and
            keep aspect ratio, otherwise will just resize to target size.
        :param thumbgen:
            Thumbnail filename generation function. All thumbnails will be saved as JPEG files,
            so there's no need to keep original file extension.

            For example::

                import os.path as op

                def thumb_name(filename):
                    name, _ = op.splitext(filename)
                    return secure_filename('%s-thumb.jpg' % name)

                class MyForm(BaseForm):
                    upload = ImageUploadField('File', thumbgen=thumb_name)

        :param thumbnail_size:
            Tuple or (width, height, force) values. If not provided, thumbnail won't be created.

            Width and height is in pixels. If `force` is set to `True`, will try to fit image into dimensions and
            keep aspect ratio, otherwise will just resize to target size.
        :param url_relative_path:
            Relative path from the root of the static directory URL. Only gets used when generating
            preview image URLs.

            For example, your model might store just file names (`relative_path` set to `None`), but
            `base_path` is pointing to subdirectory.
        :param endpoint:
            Static endpoint for images. Used by widget to display previews. Defaults to 'static'.
        """
        # Check if PIL is installed
        if Image is None:
            raise ImportError("PIL library was not found")

        self.max_size = max_size
        self.thumbnail_fn = thumbgen or thumbgen_filename
        self.thumbnail_size = thumbnail_size
        self.endpoint = endpoint
        self.image = None
        self.url_relative_path = url_relative_path

        if not allowed_extensions:
            allowed_extensions = ("gif", "jpg", "jpeg", "png", "tiff")

        super().__init__(
            label,
            validators,
            base_path=base_path,
            relative_path=relative_path,
            namegen=namegen,
            allowed_extensions=allowed_extensions,
            permission=permission,
            **kwargs,
        )

    def pre_validate(self, form):
        super().pre_validate(form)

        if self._is_uploaded_file(self.data):
            try:
                self.image = Image.open(self.data)
            except Exception as e:
                raise ValidationError("Invalid image: %s" % e)

    # Deletion
    def _delete_file(self, filename):
        super()._delete_file(filename)

        self._delete_thumbnail(filename)

    def _delete_thumbnail(self, filename):
        path = self._get_path(self.thumbnail_fn(filename))

        if op.exists(path):
            os.remove(path)

    # Saving
    def _save_file(self, data, filename):
        path = self._get_path(filename)

        if not op.exists(op.dirname(path)):
            os.makedirs(os.path.dirname(path), self.permission | 0o111)

        # Figure out format
        filename, format = self._get_save_format(filename, self.image)

        if self.image and (self.image.format != format or self.max_size):
            if self.max_size:
                image = self._resize(self.image, self.max_size)
            else:
                image = self.image

            self._save_image(image, self._get_path(filename), format)
        else:
            data.seek(0)
            data.save(self._get_path(filename))

        self._save_thumbnail(data, filename, format)

        return filename

    def _save_thumbnail(self, data, filename, format):
        if self.image and self.thumbnail_size:
            path = self._get_path(self.thumbnail_fn(filename))

            self._save_image(
                self._resize(self.image, self.thumbnail_size), path, format
            )

    def _resize(self, image, size):
        (width, height, force) = size

        if image.size[0] > width or image.size[1] > height:
            if force:
                return ImageOps.fit(
                    self.image, (width, height), Image.Resampling.LANCZOS
                )
            else:
                thumb = self.image.copy()
                thumb.thumbnail((width, height), Image.Resampling.LANCZOS)
                return thumb

        return image

    def _save_image(self, image, path, format="JPEG"):
        # New Pillow versions require RGB format for JPEGs
        if format == "JPEG" and image.mode != "RGB":
            image = image.convert("RGB")
        elif image.mode not in ("RGB", "RGBA"):
            image = image.convert("RGBA")

        with open(path, "wb") as fp:
            image.save(fp, format)

    def _get_save_format(self, filename, image):
        if image.format not in self.keep_image_formats:
            name, ext = op.splitext(filename)
            filename = "%s.jpg" % name
            return filename, "JPEG"

        return filename, image.format
