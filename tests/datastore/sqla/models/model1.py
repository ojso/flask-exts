from enum import Enum
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy import cast
from . import db


class EnumChoices(Enum):
    first = 1
    second = 2


class Model1(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    test1 = db.Column(db.String(20))
    test2 = db.Column(db.Unicode(20))
    test3 = db.Column(db.Text)
    test4 = db.Column(db.Text)
    bool_field = db.Column(db.Boolean)
    date_field = db.Column(db.Date)
    time_field = db.Column(db.Time)
    datetime_field = db.Column(db.DateTime)
    email_field = db.Column(db.String)
    enum_field = db.Column(db.Enum("model1_v1", "model1_v2"), nullable=True)
    enum_type_field = db.Column(db.Enum(EnumChoices), nullable=True)
    choice_field = db.Column(db.String, nullable=True)

    def __init__(
        self,
        test1=None,
        test2=None,
        test3=None,
        test4=None,
        bool_field=False,
        date_field=None,
        time_field=None,
        datetime_field=None,
        choice_field=None,
        enum_field=None,
        enum_type_field=None,
    ):
        self.test1 = test1
        self.test2 = test2
        self.test3 = test3
        self.test4 = test4
        self.bool_field = bool_field
        self.date_field = date_field
        self.time_field = time_field
        self.datetime_field = datetime_field
        self.choice_field = choice_field
        self.enum_field = enum_field
        self.enum_type_field = enum_type_field

    def __str__(self):
        return str(self.test1)


class Model2(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    string_field = db.Column(db.String)
    string_field_default = db.Column(db.Text, nullable=False, default="")
    string_field_empty_default = db.Column(db.Text, nullable=False, default="")
    int_field = db.Column(db.Integer)
    bool_field = db.Column(db.Boolean)
    enum_field = db.Column(db.Enum("model2_v1", "model2_v2"), nullable=True)
    float_field = db.Column(db.Float)

    # Relation
    model1_id = db.Column(db.Integer, db.ForeignKey(Model1.id))
    model1 = db.relationship(lambda: Model1, backref="model2")

    def __init__(
        self,
        string_field=None,
        int_field=None,
        bool_field=None,
        model1=None,
        float_field=None,
        string_field_default=None,
        string_field_empty_default=None,
    ):
        self.string_field = string_field
        self.int_field = int_field
        self.bool_field = bool_field
        self.model1 = model1
        self.float_field = float_field
        self.string_field_default = string_field_default
        self.string_field_empty_default = string_field_empty_default


class Model3(db.Model):
    def __init__(self, id=None, val1=None):
        self.id = id
        self.val1 = val1

    id = db.Column(db.String(20), primary_key=True)
    val1 = db.Column(db.String(20))


class ModelHybrid(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    width = db.Column(db.Integer)
    height = db.Column(db.Integer)

    firstname = db.Column(db.String)
    lastname = db.Column(db.String)

    @hybrid_property
    def fullname(self):
        return "{} {}".format(self.firstname, self.lastname)

    @hybrid_property
    def number_of_pixels(self):
        return self.width * self.height

    @hybrid_property
    def number_of_pixels_str(self):
        return str(self.number_of_pixels())

    @number_of_pixels_str.expression
    def number_of_pixels_str(cls):
        return cast(cls.width * cls.height, db.String)


class ModelHybrid2(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    owner_id = db.Column(
        db.Integer, db.ForeignKey("model_hybrid.id", ondelete="CASCADE")
    )
    owner = db.relationship("ModelHybrid", backref=db.backref("tiles"), uselist=False)


class ModelNoint(db.Model):
    id = db.Column(db.String, primary_key=True)
    test = db.Column(db.String)


class ModelForm(db.Model):
    id = db.Column(db.String, primary_key=True)
    int_field = db.Column(db.Integer)
    datetime_field = db.Column(db.DateTime)
    text_field = db.Column(db.UnicodeText)
    excluded_column = db.Column(db.String)


class ModelChild(db.Model):
    id = db.Column(db.String, primary_key=True)
    model_id = db.Column(db.Integer, db.ForeignKey(ModelForm.id))
    model = db.relationship(ModelForm, backref="backref")
    enum_field = db.Column(db.Enum("model1_v1", "model1_v2"), nullable=True)
    choice_field = db.Column(db.String, nullable=True)

class ModelMult(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    val2 = db.Column(db.String(20))

    first_id = db.Column(db.Integer, db.ForeignKey(Model1.id))
    first = db.relationship(Model1, backref="first", foreign_keys=[first_id])

    second_id = db.Column(db.Integer, db.ForeignKey(Model1.id))
    second = db.relationship(Model1, backref="second", foreign_keys=[second_id])

class ModelOnetoone1(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    test = db.Column(db.String)

class ModelOnetoone2(db.Model):
    id = db.Column(db.Integer, primary_key=True)

    model1_id = db.Column(db.Integer, db.ForeignKey(ModelOnetoone1.id))
    model1 = db.relationship(
        ModelOnetoone1, backref=db.backref("model2", uselist=False)
    )
    