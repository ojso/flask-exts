import io
from types import SimpleNamespace

import pytest
from werkzeug.datastructures import FileStorage
from wtforms.validators import ValidationError

from flask_exts.forms.validators.file import FileSize


class UnreadableStream(io.BytesIO):
    def read(self, *args, **kwargs):
        raise AssertionError("FileSize must not read the file to measure its size")


def make_field(file_storage):
    return SimpleNamespace(data=file_storage, gettext=lambda message: message)


def test_rejects_file_over_content_length_without_reading():
    upload = FileStorage(
        stream=UnreadableStream(b"small"),
        filename="large.bin",
        content_length=2 * 1024,
    )

    validator = FileSize(max_size=1024)

    with pytest.raises(ValidationError):
        validator(None, make_field(upload))

    assert upload.stream.tell() == 0


def test_measures_stream_without_content_length_and_resets_position():
    upload = FileStorage(stream=io.BytesIO(b"12345"), filename="sample.bin")
    upload.stream.seek(2)

    validator = FileSize(max_size=4)

    with pytest.raises(ValidationError):
        validator(None, make_field(upload))

    assert upload.stream.tell() == 0


def test_accepts_file_inside_limits_and_resets_position():
    upload = FileStorage(stream=io.BytesIO(b"1234"), filename="sample.bin")
    upload.stream.seek(3)

    FileSize(min_size=1, max_size=4)(None, make_field(upload))

    assert upload.stream.tell() == 0
