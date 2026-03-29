from wtforms.widgets import FileInput

class ImageInput(FileInput):
    field_flags = {"accept": "image/*"}
