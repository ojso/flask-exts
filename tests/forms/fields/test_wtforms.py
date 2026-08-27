from wtforms import Form
from wtforms.fields import (
    StringField,
    FormField,
    FieldList,
)
from wtforms.fields.core import UnboundField
from tests.forms.common import DummyPostData


class F(Form):
    a = StringField()
    b = StringField()


def test_field():
    # UnboundField
    # print(type(F.a))
    # print(F.a)
    assert isinstance(F.a, UnboundField)
    assert F.a.field_class == StringField

    # bind when a form instance
    f = F()
    # print(type(f.a))
    assert not isinstance(f.a, UnboundField)
    assert isinstance(f.a, StringField)


def test_formfield():
    class F2(Form):
        a = FormField(F)

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
    class F3(Form):
        a = FieldList(StringField())

    f = F3()
    assert f.a.entries == []
    assert len(f.a.data) == 0

    for k in range(2):
        f.a.append_entry()
    for k in range(2):
        f.a.append_entry(k)
    assert len(f.a.entries) == 4
    assert len(f.a.data) == 4
    # widget
    assert f.a() == (
        '<ul id="a">'
        '<li><label for="a-0">A-0</label> <input id="a-0" name="a-0" type="text" value=""></li>'
        '<li><label for="a-1">A-1</label> <input id="a-1" name="a-1" type="text" value=""></li>'
        '<li><label for="a-2">A-2</label> <input id="a-2" name="a-2" type="text" value="0"></li>'
        '<li><label for="a-3">A-3</label> <input id="a-3" name="a-3" type="text" value="1"></li>'
        "</ul>"
    )
    # data
    data = ["foo", "bar", "baz"]
    f = F3(a=data)
    a = f.a
    assert len(a.entries) == 3
    assert a.entries[1].data == "bar"
    assert a.entries[1].name == "a-1"
    assert a.data == data
    # formdata
    formdata = DummyPostData(
        {"a-0": ["foo"], "a-3": ["bar"], "a-4": [""], "a-7": ["qux"]}
    )
    f = F3(formdata)
    assert len(f.a.entries) == 4
    assert f.a.data == ["foo", "bar", "", "qux"]
    assert f.a.entries[1].name == "a-3"
    assert f.a.entries[1].data == "bar"
    assert f.a.entries[3].name == "a-7"
    assert f.a.entries[3].data == "qux"


def test_fieldlist_subform():
    class F4(Form):
        a = FieldList(FormField(F))

    f = F4()
    assert f.a.entries == []
    # data
    data = [{"a": "foo", "b": "bar"}, {"a": "baz", "b": "qux"}]
    f = F4(a=data)
    assert f.a.data == data
    # widget
    # print(f.a())
    assert f.a() == (
        '<ul id="a">'
        '<li><label for="a-0">A-0</label> <table id="a-0">'
        '<tr><th><label for="a-0-a">A</label></th><td><input id="a-0-a" name="a-0-a" type="text" value="foo"></td></tr>'
        '<tr><th><label for="a-0-b">B</label></th><td><input id="a-0-b" name="a-0-b" type="text" value="bar"></td></tr>'
        "</table></li>"
        '<li><label for="a-1">A-1</label> <table id="a-1">'
        '<tr><th><label for="a-1-a">A</label></th><td><input id="a-1-a" name="a-1-a" type="text" value="baz"></td></tr>'
        '<tr><th><label for="a-1-b">B</label></th><td><input id="a-1-b" name="a-1-b" type="text" value="qux"></td></tr>'
        "</table></li>"
        "</ul>"
    )
    # formdata
    formdata = DummyPostData({"a-0-a": ["bar"], "a-1-a": ["baz"], "a-1-b": ["qux"]})
    f = F4(formdata)
    assert f.a.data == [{"a": "bar", "b": None}, {"a": "baz", "b": "qux"}]
