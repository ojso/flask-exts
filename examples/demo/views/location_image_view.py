from werkzeug.utils import secure_filename
from flask import request
from flask import current_app
from wtforms.fields import FileField
from flask_exts.admin.sqla.ajax import QueryAjaxModelLoader
from flask_exts.template.widgets.render_template import RenderTemplateWidget
from flask_exts.admin.model.form import InlineFormAdmin
from flask_exts.admin.sqla import ModelView
from flask_exts.admin.sqla.form import InlineModelConverter
from flask_exts.template.fields.sqla import InlineModelFormList
from ..models.location_image import ImageType, Location, LocationImage
from ..file_op import save_image


# This widget uses custom template for inline field list
class CustomInlineFieldListWidget(RenderTemplateWidget):
    def __init__(self):
        super().__init__("field_list.html")


# This InlineModelFormList will use our custom widget and hide row controls
class CustomInlineModelFormList(InlineModelFormList):
    widget = CustomInlineFieldListWidget()

    def display_row_controls(self, field):
        return False


# Create custom InlineModelConverter and tell it to use our InlineModelFormList
class CustomInlineModelConverter(InlineModelConverter):
    inline_field_list_type = CustomInlineModelFormList


# Customized inline form handler
class LocationImageInlineModelForm(InlineFormAdmin):
    form_excluded_columns = ("path",)

    form_label = "Image"

    # Setup AJAX lazy-loading for the ImageType inside the inline model
    form_ajax_refs = {
        "image_type": QueryAjaxModelLoader(
            name="image_type",
            model=ImageType,
            fields=("name",),
            order_by="name",
            placeholder="Please use an AJAX query to select an image type for the image",
            minimum_input_length=0,
        )
    }

    def __init__(self):
        super().__init__(LocationImage)

    def postprocess_form(self, form_class):
        form_class.upload = FileField("Image")
        return form_class

    def on_model_change(self, form, model, is_created):
        file_data = request.files.get(form.upload.name)

        if file_data:
            model.path = secure_filename(file_data.filename)
            save_image(file_data, model.path)


# Administrative class
class LocationView(ModelView):
    inline_model_form_converter = CustomInlineModelConverter

    inline_models = (LocationImageInlineModelForm(),)

    def __init__(self):
        super().__init__(Location, name="Locations")


locationview = LocationView()
