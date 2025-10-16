from flask import render_template_string
from wtforms import IntegerRangeField, DecimalRangeField
from flask_exts.template.form.flask_form import FlaskForm
from flask_exts.template.fields import SwitchField


def test_switch_field(app, client):

    class TestForm(FlaskForm):
        remember = SwitchField("Remember me", description="Just check this")

    @app.route("/switch")
    def test_switch():
        form = TestForm()
        return render_template_string(
            """
        {% from 'bootstrap5/form.html' import render_form %}
        {{ render_form(form) }}
        """,
            form=form,
        )

    rv = client.get("/switch")
    assert "Remember me" in rv.text
    assert "form-check form-switch" in rv.text
    assert 'role="switch"' in rv.text
    assert (
        '<small class="form-text text-body-secondary">Just check this</small>' in rv.text
    )


# test render IntegerRangeField and DecimalRangeField
def test_range_fields(app, client):

    class TestForm(FlaskForm):
        decimal_slider = DecimalRangeField()
        integer_slider = IntegerRangeField(render_kw={"min": "0", "max": "4"})

    @app.route("/range")
    def test_range():
        form = TestForm()
        return render_template_string(
            """
            {% from 'bootstrap5/form.html' import render_form %}
            {{ render_form(form) }}
            """,
            form=form,
        )

    rv = client.get("/range")
    assert "Decimal Slider" in rv.text
    assert "Integer Slider" in rv.text
    assert "form-range" in rv.text


def test_form_group_class(app, client, hello_form):
    @app.route("/default")
    def test_default():
        form = hello_form()
        return render_template_string(
            """
            {% from 'bootstrap5/form.html' import render_form %}
            {{ render_form(form) }}
            """,
            form=form,
        )

    @app.route("/custom")
    def test_custom():
        form = hello_form()
        return render_template_string(
            """
            {% from 'bootstrap5/form.html' import render_form %}
            {{ render_form(form, form_group_classes='mb-2') }}
            """,
            form=form,
        )

    rv = client.get("/default")
    assert '<div class="mb-3' in rv.text

    rv = client.get("/custom")
    assert '<div class="mb-3' not in rv.text
    assert '<div class="mb-2' in rv.text


def test_form_group_class_config(app, client, hello_form):
    @app.route("/config")
    def test_config():
        form = hello_form()
        return render_template_string(
            """
            {% from 'bootstrap5/form.html' import render_form %}
            {{ render_form(form) }}
            """,
            form=form,
        )

    rv = client.get("/config")
    assert '<div class="mb-3' in rv.text



def test_form_inline_classes(app, client, hello_form):
    @app.route("/default")
    def test_default():
        form = hello_form()
        return render_template_string(
            """
            {% from 'bootstrap5/form.html' import render_form %}
            {{ render_form(form, form_type='inline') }}
            """,
            form=form,
        )

    @app.route("/custom")
    def test_custom():
        form = hello_form()
        return render_template_string(
            """
            {% from 'bootstrap5/form.html' import render_form %}
            {{ render_form(form, form_type='inline', form_inline_classes='custom-inline-classes') }}
            """,
            form=form,
        )

    rv = client.get("/default")
    assert '<div class="mb-3' not in rv.text
    assert '<div class="col-12' in rv.text
    assert "row row-cols-lg-auto g-3 align-items-center" in rv.text
    assert '<label class="sr-only' not in rv.text
    assert '<label class="visually-hidden' in rv.text

    rv = client.get("/custom")
    assert "row row-cols-lg-auto g-3 align-items-center" not in rv.text
    assert "custom-inline-classes" in rv.text


def test_form_inline_classes_config(app, client, hello_form):
    @app.route("/config")
    def test_config():
        form = hello_form()
        return render_template_string(
            """
            {% from 'bootstrap5/form.html' import render_form %}
            {{ render_form(form, form_type='inline') }}
            """,
            form=form,
        )

    rv = client.get("/config")
    assert "row row-cols-lg-auto g-3 align-items-center" in rv.text
