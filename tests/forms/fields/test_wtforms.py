from wtforms import Form
from wtforms.fields import (
    StringField,
    FormField,
    FieldList,
)
from tests.forms.common import DummyPostData


class F(Form):
    a = StringField()
    b = StringField()


class F2(Form):
    a = FormField(F)


class F3(Form):
    a = FieldList(StringField())


class F4(Form):
    a = FieldList(FormField(F))


def test_formfield():
    f = F2()
    # name
    assert [x.name for x in f.a] == ["a-a", "a-b"]
    # data
    f = F2(DummyPostData({"a-a": ["moo"]}))
    assert f.a.form.a.name == "a-a"
    assert f.a["a"].data == "moo"
    assert f.a["b"].data is None
    # widget
    f = F2()
    assert f.a() == (
        '<table id="a">'
        '<tr><th><label for="a-a">A</label></th>'
        '<td><input id="a-a" name="a-a" type="text" value=""></td></tr>'
        '<tr><th><label for="a-b">B</label></th>'
        '<td><input id="a-b" name="a-b" type="text" value=""></td></tr>'
        "</table>"
    )


def test_fieldlist():
    f = F3()
    assert f.a.entries == []
    # data
    data = ["foo", "bar", "baz"]
    f = F3(a=data)
    a = f.a
    assert len(a.entries) == 3
    assert a.entries[1].data == "bar"
    assert a.entries[1].name == "a-1"
    assert a.data == data
    #
    pdata = DummyPostData({"a-0": ["foo"], "a-3": ["bar"], "a-4": [""], "a-7": ["qux"]})
    f = F3(pdata)
    assert len(f.a.entries) == 4
    assert f.a.data == ["foo", "bar", "", "qux"]
    assert f.a.entries[1].name == "a-3"
    assert f.a.entries[1].data == "bar"
    assert f.a.entries[3].name == "a-7"
    assert f.a.entries[3].data == "qux"


def test_fieldlist_subform():
    f = F4()
    assert f.a.entries == []
    # data
    data = [{"a": "foo"}]
    f = F4(a=data)
    assert f.a.data == [{"a": "foo", "b": None}]
    # post
    pdata = DummyPostData(
        {"a-0-a": ["bar"], "a-1-a": ["baz"], "a-1-b": ["qux"]}
    )
    form = F4(pdata, a=data)
    assert form.a.data == [{"a": "bar", "b": None}, {"a": "baz", "b": "qux"}]
