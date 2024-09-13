=======
fields
=======

FileUpload
==================

.. module:: flask_exts.forms.fields

The FileUploadField class
----------------------------------

.. class:: FileUploadField

    Example usage::

        from flask_exts.forms.form import BaseForm
        from flask_exts.forms.fields import FileUploadField

        class TestForm(BaseForm):
            upload = FileUploadField("Upload", base_path=path)

The FileUploadField class
----------------------------------

.. class:: ImageUploadField

    Example usage::

        from flask_exts.forms.fields import ImageUploadField

        class TestForm(BaseForm):
            upload = ImageUploadField(
                "Upload", base_path=path, thumbnail_size=(100, 100, True)
            )

