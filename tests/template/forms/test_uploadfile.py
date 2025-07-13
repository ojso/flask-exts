import pytest
import os
import os.path as op
from io import BytesIO
from wtforms import Form
from flask_exts.template.form.flask_form import FlaskForm
from flask_exts.template.fields import FileField, ImageField
from flask_exts.template.validators import FileRequired


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


def test_base_upload_file_form(app):
    path = _create_temp(app.root_path)

    class TestFlaskForm(Form):
        upload = FileField("Upload")

    class TestForm(Form):
        upload = FileField("Upload", save_path=path)

    class TestOverwriteForm(Form):
        upload = FileField("Upload", save_path=path, allow_overwrite=True)

    my_base_form = TestFlaskForm()
    assert my_base_form.upload.save_path is None
    assert my_base_form.upload.allow_overwrite == False
    assert not my_base_form.validate()
    assert len(my_base_form.upload.errors) > 0
    assert my_base_form.upload() == '<input id="upload" name="upload" type="file">'

    my_form = TestForm()
    assert my_form.upload.save_path == path
    assert my_form.upload.allow_overwrite == False
    assert my_form.validate()
    assert my_form.upload() == '<input id="upload" name="upload" type="file">'

    my_ow_form = TestOverwriteForm()
    assert my_ow_form.upload.save_path == path
    assert my_ow_form.upload.allow_overwrite == True
    assert my_form.validate()
    assert my_ow_form.upload() == '<input id="upload" name="upload" type="file">'


def test_base_upload_image_form(app):
    path = _create_temp(app.root_path)

    class TestUploadImageForm(Form):
        upload = ImageField("Upload")

    my_image_form = TestUploadImageForm()
    # print(my_image_form.upload())
    assert (
        my_image_form.upload()
        == '<input accept="image/*" id="upload" name="upload" type="file">'
    )


def test_base_upload_required_field(app):
    path = _create_temp(app.root_path)

    class TestRequiredForm(Form):
        upload = FileField("Upload", validators=[FileRequired()])

    my_required_form = TestRequiredForm()
    assert (
        my_required_form.upload()
        == '<input id="upload" name="upload" required type="file">'
    )
    # assert my_base_form.upload.save_path is None
    # assert my_base_form.upload.allow_overwrite == False
    assert not my_required_form.validate()
    # assert len(my_required_form.upload.errors) > 0
    # print(my_required_form.upload.errors)
    assert "This field is required." in my_required_form.upload.errors


def test_upload_file_field(app):
    path = _create_temp(app.root_path)

    def _remove_testfiles():
        safe_delete(path, "test1.txt")
        safe_delete(path, "test2.txt")

    class TestForm(FlaskForm):
        upload = FileField("Upload", save_path=path)

    class TestOverwriteForm(FlaskForm):
        upload = FileField("Upload", save_path=path, allow_overwrite=True)

    # Check upload
    app.config.update(CSRF_ENABLED=False)
    with app.test_request_context(
        method="POST", data={"upload": (BytesIO(b"Hello World 1"), "test1.txt")}
    ):
        my_form = TestOverwriteForm()
        assert my_form.validate()
        assert my_form.upload.data.filename == "test1.txt"
        my_form.upload.save_file()
        fpath = op.join(path, "test1.txt")
        assert op.exists(fpath)
        with open(fpath) as f:
            txt = f.read()
        # print(txt)
        assert txt == "Hello World 1"
    # Check replace
    with app.test_request_context(
        method="POST", data={"upload": (BytesIO(b"Hello World 2"), "test1.txt")}
    ):
        my_form = TestOverwriteForm()

        assert my_form.validate()
        assert my_form.upload.data.filename == "test1.txt"
        my_form.upload.save_file()
        fpath = op.join(path, "test1.txt")
        assert op.exists(fpath)
        with open(fpath) as f:
            txt = f.read()
        assert txt == "Hello World 2"

    # Check overwrite
    with app.test_request_context(
        method="POST", data={"upload": (BytesIO(b"Hello World 2"), "test1.txt")}
    ):
        my_form = TestForm()
        assert not my_form.validate()
        assert my_form.upload.data.filename == "test1.txt"
        with pytest.raises(FileExistsError, match=r".*exists.*"):
            my_form.upload.save_file()

    _remove_testfiles()
