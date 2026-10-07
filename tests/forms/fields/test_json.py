from wtforms.form import Form

from flask_exts.forms.fields import JSONField
from tests.forms.common import DummyPostData


def test_json_field():
    class F(Form):
        a = JSONField()

    f = F()
    # print(f.a())
    assert f.a()=='<textarea id="a" name="a">\r\n</textarea>'
    # data
    f = F(a=[1,2,3])
    assert f.validate()
    # print(f.a())
    assert f.a()=='<textarea id="a" name="a">\r\n[1, 2, 3]</textarea>'
    f = F(a={"xyz":"abc"})
    assert f.validate()
    # print(f.a())
    assert f.a()=='<textarea id="a" name="a">\r\n{&#34;xyz&#34;: &#34;abc&#34;}</textarea>'

    #formdata
    formdata = DummyPostData(a="[1,2,3]")
    f = F(formdata)
    assert f.validate()
    assert f.a()=='<textarea id="a" name="a">\r\n[1, 2, 3]</textarea>'
    formdata = DummyPostData(a='{"a":1}')
    f = F(formdata)
    assert f.validate()
    # print(f.a())
    assert f.a()=='<textarea id="a" name="a">\r\n{&#34;a&#34;: 1}</textarea>'

