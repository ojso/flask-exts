from wtforms.fields import StringField
from wtforms.fields import FieldList
from wtforms.form import Form
from flask_exts.forms.form import FlaskForm


class F(Form):
    txt = FieldList(StringField())


class flaskF(FlaskForm):
    txt = FieldList(StringField())


def test_field_list_string():
    f = F()
    # print(f.txt.data)
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


def test_flask_field_list_string(app):

    with app.test_request_context(
        method="POST", data={"txt-0": "1", "txt-1": "2", "txt-2": "3"}
    ):
        f = flaskF()
        # print(f.txt.data)
        assert len(f.txt.data) == 3
        assert '1' in f.txt.data
        assert '2' in f.txt.data
        assert '3' in f.txt.data
