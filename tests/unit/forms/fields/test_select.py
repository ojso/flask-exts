from wtforms import Form
from wtforms.fields import Choice, SelectChoice

from flask_exts.forms.fields import ChoiceField


def test_tuple_choices_do_not_warn(post_data_factory):
    class F(Form):
        a = ChoiceField(choices=[("x", "X"), ("y", "Y")])

    f = F()
    assert len(f.a.choices) == 2
    assert f.a.choices[0].value == "x"
    assert f.a.choices[0].label == "X"
    assert f.a.choices[1].value == "y"
    assert f.a.choices[1].label == "Y"
    assert f.a() == (
        '<select id="a" name="a">'
        '<option value="x">X</option>'
        '<option value="y">Y</option>'
        "</select>"
    )

    formdata = post_data_factory({"a": "y"})
    f = F(formdata)
    assert f.validate()
    assert f.a.data == "y"
    assert f.a() == (
        '<select id="a" name="a">'
        '<option value="x">X</option>'
        '<option selected value="y">Y</option>'
        "</select>"
    )


def test_select_choice_choices():
    class F(Form):
        a = ChoiceField(
            choices=[SelectChoice("x", "X"), SelectChoice("y", "Y")],
        )

    f = F()
    assert f.a() == (
        '<select id="a" name="a">'
        '<option value="x">X</option>'
        '<option value="y">Y</option>'
        "</select>"
    )


def test_allow_blank(post_data_factory):
    class F(Form):
        a = ChoiceField(
            choices=[("x", "X"), ("y", "Y")],
            allow_blank=True,
            blank_text="Choose",
        )

    f = F()
    assert f.a.data is None
    assert f.a() == (
        '<select id="a" name="a">'
        '<option selected value="">Choose</option>'
        '<option value="x">X</option>'
        '<option value="y">Y</option>'
        "</select>"
    )

    formdata = post_data_factory({"a": ""})
    f = F(formdata)
    assert f.validate()
    assert f.a.data is None


def test_invalid_choice(post_data_factory):
    class F(Form):
        a = ChoiceField(choices=[("x", "X"), ("y", "Y")])

    formdata = post_data_factory({"a": "z"})
    f = F(formdata)
    assert not f.validate()
    assert "Not a valid choice" in f.a.errors[0]


def test_no_choices():
    class F(Form):
        a = ChoiceField()

    f = F()
    assert f.a.choices is None
    assert f.a() == '<select id="a" name="a"></select>'


def test_string_choices():
    class F(Form):
        a = ChoiceField(choices=["x", "y"])

    f = F()
    assert f.a() == (
        '<select id="a" name="a">'
        '<option value="x">x</option>'
        '<option value="y">y</option>'
        "</select>"
    )


def test_three_item_tuple_choices(post_data_factory):
    class F(Form):
        a = ChoiceField(choices=[("x", "X", {"disabled": True})])

    f = F()
    assert f.a() == (
        '<select id="a" name="a"><option disabled value="x">X</option></select>'
    )

    f = F(post_data_factory({"a": "x"}))
    assert f.validate()
    assert f.a.data == "x"


def test_dict_choices():
    class F(Form):
        a = ChoiceField(choices={"x": "X", "y": "Y"})

    f = F()
    assert all(isinstance(choice, SelectChoice) for choice in f.a.choices)
    assert f.a() == (
        '<select id="a" name="a">'
        '<option value="x">X</option>'
        '<option value="y">Y</option>'
        "</select>"
    )


def test_dict_optgroup_choices():
    class F(Form):
        a = ChoiceField(choices={"Group": {"x": "X"}})

    f = F()
    assert f.a() == (
        '<select id="a" name="a">'
        '<optgroup label="Group">'
        '<option value="x">X</option>'
        "</optgroup>"
        "</select>"
    )


def test_legacy_dict_optgroup_list_choices():
    class F(Form):
        a = ChoiceField(choices={"Group": [("x", "X")]})

    f = F()
    assert f.a() == (
        '<select id="a" name="a">'
        '<optgroup label="Group">'
        '<option value="x">X</option>'
        "</optgroup>"
        "</select>"
    )


def test_callable_choices():
    def choices():
        return [("x", "X")]

    class F(Form):
        a = ChoiceField(choices=choices)

    f = F()
    assert f.a() == ('<select id="a" name="a"><option value="x">X</option></select>')


def test_render_kw_preserved():
    class F(Form):
        a = ChoiceField(choices=[SelectChoice("x", "X", {"data-k": "v"})])

    f = F()
    assert f.a() == (
        '<select id="a" name="a"><option data-k="v" value="x">X</option></select>'
    )


def test_choice_input_is_converted():
    class F(Form):
        a = ChoiceField(choices=[Choice("x", "X", False, {"data-k": "1"})])

    f = F()
    assert isinstance(f.a.choices[0], SelectChoice)
    assert f.a() == (
        '<select id="a" name="a"><option data-k="1" value="x">X</option></select>'
    )


def test_optgroup_with_blank_choice():
    class F(Form):
        a = ChoiceField(
            choices=[SelectChoice("x", "X", optgroup="Group")],
            allow_blank=True,
            blank_text="Choose",
        )

    f = F()
    assert f.a() == (
        '<select id="a" name="a">'
        '<option selected value="">Choose</option>'
        '<optgroup label="Group">'
        '<option value="x">X</option>'
        "</optgroup>"
        "</select>"
    )


def test_choices_assigned_after_init():
    class F(Form):
        a = ChoiceField()

    f = F()
    f.a.choices = [("x", "X")]
    assert f.a() == ('<select id="a" name="a"><option value="x">X</option></select>')


def test_coerce_type_error_is_validation_error(post_data_factory):
    def coerce(value):
        raise TypeError("boom")

    class F(Form):
        a = ChoiceField(choices=[("x", "X")], coerce=coerce)

    f = F(post_data_factory({"a": "x"}))
    assert not f.validate()
    assert "could not coerce" in f.a.errors[0]
