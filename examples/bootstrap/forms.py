from wtforms.validators import DataRequired, Length, Regexp
from wtforms.fields import *
from flask_exts.template.fields import SwitchField
from flask_exts.template.form.flask_form import FlaskForm


class ExampleForm(FlaskForm):
    """An example form that contains all the supported bootstrap style form fields."""

    date = DateField(
        description="We'll never share your email with anyone else."
    )  # add help text with `description`
    datetime = DateTimeField(
        render_kw={"placeholder": "this is a placeholder"}
    )  # add HTML attribute with `render_kw`
    datetime_local = DateTimeLocalField()
    time = TimeField()
    month = MonthField()
    color = ColorField()
    floating = FloatField()
    integer = IntegerField()
    decimal_slider = DecimalRangeField()
    integer_slider = IntegerRangeField(render_kw={"min": "0", "max": "4"})
    email = EmailField()
    url = URLField()
    telephone = TelField()
    image = FileField(
        render_kw={"class": "my-class"}, validators=[Regexp(r".+\.jpg$")]
    )  # add your class
    option = RadioField(
        choices=[("dog", "Dog"), ("cat", "Cat"), ("bird", "Bird"), ("alien", "Alien")]
    )
    select = SelectField(
        choices=[("dog", "Dog"), ("cat", "Cat"), ("bird", "Bird"), ("alien", "Alien")]
    )
    select_multiple = SelectMultipleField(
        choices=[("dog", "Dog"), ("cat", "Cat"), ("bird", "Bird"), ("alien", "Alien")]
    )
    bio = TextAreaField()
    search = SearchField()  # will autocapitalize on mobile
    title = StringField()  # will not autocapitalize on mobile
    secret = PasswordField()
    remember = BooleanField("Remember me")
    submit = SubmitField()


class HelloForm(FlaskForm):
    username = StringField("Username", validators=[DataRequired(), Length(1, 20)])
    password = PasswordField("Password", validators=[DataRequired(), Length(8, 150)])
    remember = BooleanField("Remember me")
    submit = SubmitField()


class ButtonForm(FlaskForm):
    username = StringField("Username", validators=[DataRequired(), Length(1, 20)])
    confirm = SwitchField("Confirmation")
    submit = SubmitField()
    delete = SubmitField()
    cancel = SubmitField()


class TelephoneForm(FlaskForm):
    country_code = IntegerField("Country Code")
    area_code = IntegerField("Area Code/Exchange")
    number = StringField("Number")


class IMForm(FlaskForm):
    protocol = SelectField(choices=[("aim", "AIM"), ("msn", "MSN")])
    username = StringField()


class ContactForm(FlaskForm):
    first_name = StringField()
    last_name = StringField()
    mobile_phone = FormField(TelephoneForm)
    office_phone = FormField(TelephoneForm)
    emails = FieldList(StringField("Email"), min_entries=3)
    im_accounts = FieldList(FormField(IMForm), min_entries=2)


class BootswatchForm(FlaskForm):
    """Form to test Bootswatch."""

    # DO NOT EDIT! Use list-bootswatch.py to generate the Radiofield below.
    theme_name = RadioField(
        default="default",
        choices=[
            ("default", "none"),
            ("cerulean", "Cerulean 4.6.1"),
            ("cosmo", "Cosmo 4.6.1"),
            ("cyborg", "Cyborg 4.6.1"),
            ("darkly", "Darkly 4.6.1"),
            ("flatly", "Flatly 4.6.1"),
            ("journal", "Journal 4.6.1"),
            ("litera", "Litera 4.6.1"),
            ("lumen", "Lumen 4.6.1"),
            ("lux", "Lux 4.6.1"),
            ("materia", "Materia 4.6.1"),
            ("minty", "Minty 4.6.1"),
            ("pulse", "Pulse 4.6.1"),
            ("sandstone", "Sandstone 4.6.1"),
            ("simplex", "Simplex 4.6.1"),
            ("sketchy", "Sketchy 4.6.1"),
            ("slate", "Slate 4.6.1"),
            ("solar", "Solar 4.6.1"),
            ("spacelab", "Spacelab 4.6.1"),
            ("superhero", "Superhero 4.6.1"),
            ("united", "United 4.6.1"),
            ("yeti", "Yeti 4.6.1"),
        ],
    )
    submit = SubmitField()
