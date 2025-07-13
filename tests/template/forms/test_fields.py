from wtforms.form import Form
from wtforms.fields import StringField
from wtforms.fields import FieldList
from flask_exts.template.fields import JSONField
from flask_exts.template.fields import DateTimePickerField


class DummyPostData(dict):
    def getlist(self, key):
        v = self[key]
        if not isinstance(v, (list, tuple)):
            v = [v]
        return v


def test_json_field():
    class F(Form):
        json_field = JSONField()

    formdata = DummyPostData(
        json_field="[1,2,3]",
    )

    f = F(formdata)
    assert f.validate()

    json_field_text = f.json_field()
    assert '<textarea id="json_field" name="json_field">' in json_field_text
    assert "[1, 2, 3]</textarea>" in json_field_text


def test_datetime_field():
    class F(Form):
        datetime_field = DateTimePickerField()

    formdata = DummyPostData(
        datetime_field="2000-01-01 12:12:12",
    )

    f = F(formdata)
    assert f.validate()

    datetime_field_text = f.datetime_field()
    assert "<input" in datetime_field_text
    assert (
        'data-date-format="YYYY-MM-DD HH:mm:ss" data-role="datetimepicker"'
        in datetime_field_text
    )
    assert 'value="2000-01-01 12:12:12"' in datetime_field_text


def test_field_list_string():
    class F(Form):
        txt = FieldList(StringField())

    formdata = DummyPostData({"txt-0": "1", "txt-1": "2", "txt-2": "3"})

    f = F()
    assert len(f.txt.data) == 0
    for k in range(2):
        f.txt.append_entry()
    for k in range(2):
        f.txt.append_entry(k)
    # print(f.txt())
    assert '<input id="txt-0" name="txt-0" type="text" value="">' in f.txt()
    assert '<input id="txt-1" name="txt-1" type="text" value="">' in f.txt()
    assert '<input id="txt-2" name="txt-2" type="text" value="0">' in f.txt()
    assert '<input id="txt-3" name="txt-3" type="text" value="1">' in f.txt()
    # print(f.txt.data)

    f = F(formdata)
    # print(f.txt.data)
    assert len(f.txt.data) == 3
    assert "1" in f.txt.data
    assert "2" in f.txt.data
    assert "3" in f.txt.data
