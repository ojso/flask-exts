======
field
======

.. module:: flask_exts.form.fields.upload

The FileUploadField class
-----------------------------

.. class:: FileUploadField

    Example usage::

        from flask_exts.form.form.base_form import BaseForm
        from flask_exts.form.fields.upload import FileUploadField

        class TestForm(BaseForm):
            upload = FileUploadField("Upload", base_path=path)

The FileUploadField class
-----------------------------

.. class:: ImageUploadField

    Example usage::

        from flask_exts.form.fields.upload import ImageUploadField

        class TestForm(BaseForm):
            upload = ImageUploadField(
                "Upload", base_path=path, thumbnail_size=(100, 100, True)
            )

