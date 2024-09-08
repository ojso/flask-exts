import os
import os.path as op
from io import BytesIO
from flask_exts.forms.form.flask_form import FlaskForm
from flask_exts.forms.fields.upload_file import UploadFileField

def _create_temp(root_path):
    path = op.join(root_path, "tmp")
    if not op.exists(path):
        os.mkdir(path)

    return path


def safe_delete(path, name):
    try:
        os.remove(op.join(path, name))
    except:
        pass


def test_relative_path(app):
    path = _create_temp(app.root_path)

    class TestForm(FlaskForm):
        upload = UploadFileField("Upload", base_path=path)

    my_form = TestForm()
    assert my_form.upload.base_path == path


def test_upload_file_field(app):
    path = _create_temp(app.root_path)

    def _remove_testfiles():
        safe_delete(path, "test1.txt")
        safe_delete(path, "test2.txt")

    class TestForm(FlaskForm):
        upload = UploadFileField("Upload", base_path=path, allow_overwrite=True)

    class TestNoOverWriteForm(FlaskForm):
        upload = UploadFileField("Upload", base_path=path)

    # Check upload
    with app.test_request_context(
        method="POST", data={"upload": (BytesIO(b"Hello World 1"), "test1.txt")}
    ):
        my_form = TestForm()

        assert my_form.validate()
        assert my_form.upload.filename == "test1.txt"
        my_form.upload.save_file()
        assert op.exists(op.join(path, "test1.txt"))

    # Check replace
    with app.test_request_context(
        method="POST", data={"upload": (BytesIO(b"Hello World 2"), "test1.txt")}
    ):
        my_form = TestForm()

        assert my_form.validate()
        assert my_form.upload.filename == "test1.txt"
        my_form.upload.save_file()

    # Check overwrite
    
    my_form_ow = TestNoOverWriteForm()
    with app.test_request_context(
        method="POST", data={"upload": (BytesIO(b"Hullo"), "test1.txt")}
    ):
        my_form_ow = TestNoOverWriteForm()
        # my_form.upload.save_file()


    _remove_testfiles()
