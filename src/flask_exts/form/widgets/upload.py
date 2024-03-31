from urllib.parse import urljoin
from markupsafe import Markup
from wtforms.widgets import html_params
from werkzeug.datastructures import FileStorage
from flask import url_for


class FileUploadInput:
    """Renders a file input chooser field.

    You can customize `empty_template` and `data_template` members to customize look and feel.
    """

    input_type = "file"
    empty_template = "<input %(file)s>"
    data_template = (
        "<div>"
        " <input %(text)s>"
        ' <input type="checkbox" name="%(marker)s">Delete</input>'
        "</div>"
        "<input %(file)s>"
    )

    def __call__(self, field, **kwargs):
        kwargs.setdefault("id", field.id)
        kwargs.setdefault("name", field.name)

        template = self.data_template if field.data else self.empty_template

        if field.errors:
            template = self.empty_template

        if field.data and isinstance(field.data, FileStorage):
            value = field.data.filename
        else:
            value = field.data or ""

        return Markup(
            template
            % {
                "text": html_params(
                    type="text", readonly="readonly", value=value, name=field.name
                ),
                "file": html_params(type="file", value=value, **kwargs),
                "marker": "_%s-delete" % field.name,
            }
        )


class ImageUploadInput:
    """Renders a image input chooser field.

    You can customize `empty_template` and `data_template` members to customize look and feel.
    """

    input_type = "file"
    empty_template = "<input %(file)s>"
    data_template = (
        '<div class="image-thumbnail">'
        " <img %(image)s>"
        ' <input type="checkbox" name="%(marker)s">Delete</input>'
        " <input %(text)s>"
        "</div>"
        "<input %(file)s>"
    )

    def __call__(self, field, **kwargs):
        kwargs.setdefault("id", field.id)
        kwargs.setdefault("name", field.name)

        args = {
            "text": html_params(type="hidden", value=field.data, name=field.name),
            "file": html_params(type="file", **kwargs),
            "marker": "_%s-delete" % field.name,
        }

        if field.data and isinstance(field.data, str):
            url = self.get_url(field)
            args["image"] = html_params(src=url)

            template = self.data_template
        else:
            template = self.empty_template

        return Markup(template % args)

    def get_url(self, field):
        if field.thumbnail_size:
            filename = field.thumbnail_fn(field.data)
        else:
            filename = field.data

        if field.url_relative_path:
            filename = urljoin(field.url_relative_path, filename)

        return url_for(field.endpoint, filename=filename)
