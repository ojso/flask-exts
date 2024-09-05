import os
import os.path as op
from io import BytesIO
from flask import url_for
from flask_exts.forms.form.base_form import BaseForm
from flask_exts.forms.fields.upload_file import FileUploadField
from flask_exts.utils import get_form_data


def _create_temp(root_path):
    path = op.join(root_path, "tmp")
    if not op.exists(path):
        os.mkdir(path)

    inner = op.join(path, "inner")
    if not op.exists(inner):
        os.mkdir(inner)

    return path


def safe_delete(path, name):
    try:
        os.remove(op.join(path, name))
    except:
        pass


def test_upload_field(app):
    path = _create_temp(app.root_path)

    def _remove_testfiles():
        safe_delete(path, "test1.txt")
        safe_delete(path, "test2.txt")

    class TestForm(BaseForm):
        upload = FileUploadField("Upload", base_path=path)

    class TestNoOverWriteForm(BaseForm):
        upload = FileUploadField("Upload", base_path=path, allow_overwrite=False)

    class Dummy:
        pass

    my_form = TestForm()
    assert my_form.upload.base_path == path

    _remove_testfiles()

    dummy = Dummy()

    # Check upload
    with app.test_request_context(
        method="POST", data={"upload": (BytesIO(b"Hello World 1"), "test1.txt")}
    ):
        my_form = TestForm(get_form_data())

        assert my_form.validate()

        my_form.populate_obj(dummy)

        assert dummy.upload == "test1.txt"
        assert op.exists(op.join(path, "test1.txt"))

    # Check replace
    with app.test_request_context(
        method="POST", data={"upload": (BytesIO(b"Hello World 2"), "test2.txt")}
    ):
        my_form = TestForm(get_form_data())

        assert my_form.validate()
        my_form.populate_obj(dummy)

        assert dummy.upload == "test2.txt"
        assert not op.exists(op.join(path, "test1.txt"))
        assert op.exists(op.join(path, "test2.txt"))

    # Check delete
    with app.test_request_context(method="POST", data={"_upload-delete": "checked"}):

        my_form = TestForm(get_form_data())

        assert my_form.validate()

        my_form.populate_obj(dummy)
        assert dummy.upload is None

        assert not op.exists(op.join(path, "test2.txt"))

    # Check overwrite
    _remove_testfiles()
    my_form_ow = TestNoOverWriteForm()
    with app.test_request_context(
        method="POST", data={"upload": (BytesIO(b"Hullo"), "test1.txt")}
    ):
        my_form_ow = TestNoOverWriteForm(get_form_data())

        assert my_form_ow.validate()
        my_form_ow.populate_obj(dummy)
        assert dummy.upload == "test1.txt"
        assert op.exists(op.join(path, "test1.txt"))

    with app.test_request_context(
        method="POST", data={"upload": (BytesIO(b"Hullo"), "test1.txt")}
    ):
        my_form_ow = TestNoOverWriteForm(get_form_data())

        assert not my_form_ow.validate()

    _remove_testfiles()



def test_relative_path(app):
    path = _create_temp(app.root_path)

    def _remove_testfiles():
        safe_delete(path, "test1.txt")

    class TestForm(BaseForm):
        upload = FileUploadField("Upload", base_path=path, relative_path="inner/")

    class Dummy:
        pass

    my_form = TestForm()
    assert my_form.upload.base_path == path
    assert my_form.upload.relative_path == "inner/"

    _remove_testfiles()

    dummy = Dummy()

    # Check upload
    with app.test_request_context(
        method="POST", data={"upload": (BytesIO(b"Hello World 1"), "test1.txt")}
    ):
        my_form = TestForm(get_form_data())

        assert my_form.validate()

        my_form.populate_obj(dummy)

        assert dummy.upload == "inner/test1.txt"
        assert op.exists(op.join(path, "inner/test1.txt"))

        assert url_for("static", filename=dummy.upload) == "/static/inner/test1.txt"

        safe_delete(path, dummy.upload)

        
