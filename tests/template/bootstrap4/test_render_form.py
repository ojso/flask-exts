from flask import current_app, render_template_string
from wtforms import (
    BooleanField,
    FileField,
    MultipleFileField,
    PasswordField,
    RadioField,
    StringField,
    SubmitField,
    IntegerRangeField,
    DecimalRangeField,
)
from wtforms.validators import DataRequired
from flask_exts.template.form.flask_form import FlaskForm
from flask_exts.template.fields import SwitchField


def test_render_form(app, client, hello_form):
    @app.route("/form")
    def test():
        form = hello_form()
        return render_template_string(
            """
            {% from 'bootstrap4/form.html' import render_form %}
            {{ render_form(form) }}
            """,
            form=form,
        )

    rv = client.get("/form")
    assert '<input class="form-control" id="username"' in rv.text
    assert '<input class="form-control" id="password"' in rv.text


# test WTForm field description for BooleanField
def test_form_description_for_booleanfield(app, client):
    class TestForm(FlaskForm):
        remember = BooleanField("Remember me", description="Just check this")

    @app.route("/description")
    def description():
        form = TestForm()
        return render_template_string(
            """
            {% from 'bootstrap4/form.html' import render_form %}
            {{ render_form(form) }}
            """,
            form=form,
        )

    rv = client.get("/description")
    assert "Remember me" in rv.text
    assert '<small class="form-text text-muted">Just check this</small>' in rv.text



# test render SwitchField
def test_switch_field(app, client):
    class TestForm(FlaskForm):
        remember = SwitchField("Remember me", description="Just check this")

    @app.route("/switch")
    def test_switch():
        form = TestForm()
        return render_template_string(
            """
            {% from 'bootstrap4/form.html' import render_form %}
            {{ render_form(form) }}
            """,
            form=form,
        )

    rv = client.get("/switch")
    assert "Remember me" in rv.text
    assert "custom-switch" in rv.text
    assert '<small class="form-text text-muted">Just check this</small>' in rv.text



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
            {% from 'bootstrap4/form.html' import render_form %}
            {{ render_form(form) }}
            """,
            form=form,
        )

    rv = client.get("/range")
    assert "Decimal Slider" in rv.text
    assert "Integer Slider" in rv.text
    assert "form-control-range" in rv.text



# test WTForm fields for render_form and render_field
def test_render_form_enctype(app, client):
    class SingleUploadForm(FlaskForm):
        avatar = FileField("Avatar")

    class MultiUploadForm(FlaskForm):
        photos = MultipleFileField("Multiple photos")

    @app.route("/single")
    def single():
        form = SingleUploadForm()
        return render_template_string(
            """
            {% from 'bootstrap4/form.html' import render_form %}
            {{ render_form(form) }}
            """,
            form=form,
        )

    @app.route("/multi")
    def multi():
        form = SingleUploadForm()
        return render_template_string(
            """
            {% from 'bootstrap4/form.html' import render_form %}
            {{ render_form(form) }}
            """,
            form=form,
        )

    rv = client.get("/single")
    assert "multipart/form-data" in rv.text

    rv = client.get("/multi")
    assert "multipart/form-data" in rv.text


# test render_kw class for WTForms field
def test_form_render_kw_class(app, client):
    class TestForm(FlaskForm):
        username = StringField("Username")
        password = PasswordField("Password", render_kw={"class": "my-password-class"})
        submit = SubmitField(render_kw={"class": "my-awesome-class"})

    @app.route("/render_kw")
    def render_kw():
        form = TestForm()
        return render_template_string(
            """
            {% from 'bootstrap4/form.html' import render_form %}
            {{ render_form(form) }}
            """,
            form=form,
        )

    rv = client.get("/render_kw")
    assert 'class="form-control"' in rv.text
    assert 'class="form-control "' not in rv.text
    assert 'class="form-control my-password-class"' in rv.text
    assert "my-awesome-class" in rv.text
    assert "btn" in rv.text


def test_button(app, client, hello_form):
    @app.route("/form")
    def test():
        form = hello_form()
        return render_template_string(
            """
            {% from 'bootstrap4/form.html' import render_form %}
            {{ render_form(form) }}
            """,
            form=form,
        )

    @app.route("/form2")
    def test_overwrite():
        form = hello_form()
        return render_template_string(
            """
            {% from 'bootstrap4/form.html' import render_form %}
            {{ render_form(form, button_size='sm',button_style='success') }}
            """,
            form=form,
        )

    @app.route("/form3")
    def test_button_map():
        form = hello_form()
        return render_template_string(
            """
            {% from 'bootstrap4/form.html' import render_form %}
            {{ render_form(form, button_map={'submit': 'warning'}) }}
            """,
            form=form,
        )

    rv = client.get("/form")
    assert "btn-primary" in rv.text
    assert "btn-md" in rv.text

    rv = client.get("/form2")
    assert "btn-success" in rv.text
    assert "btn-sm" in rv.text

    rv = client.get("/form3")
    assert "btn-warning" in rv.text
    assert "btn-md" in rv.text


def test_error_message_for_radiofield_and_booleanfield(app, client):
    class TestForm(FlaskForm):
        remember = BooleanField("Remember me", validators=[DataRequired()])
        option = RadioField(
            choices=[
                ("dog", "Dog"),
                ("cat", "Cat"),
                ("bird", "Bird"),
                ("alien", "Alien"),
            ],
            validators=[DataRequired()],
        )

    @app.route("/error", methods=["GET", "POST"])
    def error():
        form = TestForm()
        if form.validate_on_submit():
            pass
        return render_template_string(
            """
            {% from 'bootstrap4/form.html' import render_form %}
            {{ render_form(form) }}
            """,
            form=form,
        )

    rv = client.post("/error", follow_redirects=True)
    assert "This field is required" in rv.text
