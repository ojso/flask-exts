from datetime import datetime
from wtforms.form import Form
from flask_exts.forms.fields import DateTimePickerField
from tests.forms.common import DummyPostData


def test_datetime_field():
    class F(Form):
        a = DateTimePickerField()

    f = F()
    assert f.a() == (
        '<input data-date-format="YYYY-MM-DD HH:mm:ss" data-role="datetimepicker" id="a" name="a" type="text" value="">'
    )
    assert f.a.data is None

    # formdata
    dt = datetime(2000, 1, 1, 1, 1, 1)
    assert dt.strftime("%Y-%m-%d %H:%M:%S") == "2000-01-01 01:01:01"
    formdata = DummyPostData(a="2000-01-01 01:01:01")
    f = F(formdata)
    assert f.validate()
    assert f.a() == (
        '<input data-date-format="YYYY-MM-DD HH:mm:ss" data-role="datetimepicker" id="a" name="a" type="text" value="2000-01-01 01:01:01">'
    )
    assert f.a.data == dt
