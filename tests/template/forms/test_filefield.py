from io import BytesIO
from wtforms.fields import FileField
from wtforms.fields import MultipleFileField
from wtforms.form import Form
from werkzeug.datastructures import FileStorage
from flask_exts.template.form.flask_form import FlaskForm


class F(Form):
    file = FileField()

class MultipleF(Form):
    files = MultipleFileField()

class FlaskF(FlaskForm):
    file = FileField()


class FlaskMultipleF(FlaskForm):
    files = MultipleFileField()


def test_filefield_without_file_input():
    f = F()
    assert f.file.raw_data is None
    assert f.file.data is None
    assert f.file() == '<input id="file" name="file" type="file">'

def test_multiplefilefield_without_file_input():
    mf = MultipleF()
    assert mf.files.raw_data is None
    assert mf.files.data is None
    assert mf.files() == '<input id="files" multiple name="files" type="file">'


def test_filefield_with_file_input(app):
    with app.test_request_context(
        method="POST", data={"file": (BytesIO(b"Hello World"), "test.txt")}
    ):
        f = FlaskF()
        # print(f.file)
        # print(f.file.raw_data)
        # print(f.file.data)
        # print(f.file())
        assert isinstance(f.file.raw_data, list)
        assert len(f.file.raw_data) == 1
        assert isinstance(f.file.data, FileStorage)
        assert f.file.data.filename == "test.txt"
        # print(f.file.data.read())
        assert f.file.data.read() == b"Hello World"


def test_filefield_with_multiplefile_input(app):
    with app.test_request_context(
        method="POST",
        data={
            "file": [
                (BytesIO(b"Hello World"), "test.txt"),
                (BytesIO(b"Hello World 2"), "test2.txt"),
            ]
        },
    ):
        f = FlaskF()
        assert isinstance(f.file.raw_data, list)
        assert len(f.file.raw_data) == 2
        assert isinstance(f.file.data, FileStorage)
        assert f.file.data.filename == "test.txt"
        assert f.file.data.read() == b"Hello World"


def test_multiplefilefield_with_multiplefile_input(app):
    with app.test_request_context(
        method="POST",
        data={
            "files": [
                (BytesIO(b"Hello World"), "test.txt"),
                (BytesIO(b"Hello World 2"), "test2.txt"),
            ]
        },
    ):
        f = FlaskMultipleF()
        assert isinstance(f.files.raw_data, list)
        assert len(f.files.raw_data) == 2
        # print(f.files.data)
        assert len(f.files.data) == 2
        f1 = f.files.data[0]
        f2 = f.files.data[1]
        # print(f1)
        # print(f2)
        assert isinstance(f1, FileStorage)
        assert f1.filename == "test.txt"
        assert f1.read() == b"Hello World"
        assert isinstance(f2, FileStorage)
        assert f2.filename == "test2.txt"
        assert f2.read() == b"Hello World 2"
