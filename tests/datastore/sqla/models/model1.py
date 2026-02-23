import enum
from datetime import datetime, date, time
from .. import db
from .. import Mapped
from .. import mapped_column
from .. import ForeignKey
from .. import relationship
from .. import hybrid_property
from .. import cast
from .. import Integer
from .. import Boolean
from .. import String
from .. import TEXT
from .. import Enum
from .. import Float
from .. import DateTime

class EnumChoices(enum.Enum):
    first = 1
    second = 2


class Model1(db.Model):
    __tablename__ = "model1"

    id: Mapped[int] = mapped_column(primary_key=True)
    test1: Mapped[str]
    test2: Mapped[str]
    test3: Mapped[str] = mapped_column(TEXT)
    test4: Mapped[str] = mapped_column(TEXT)
    bool_field: Mapped[bool]
    date_field: Mapped[date]
    time_field: Mapped[time]
    datetime_field: Mapped[datetime]
    email_field: Mapped[str]
    enum_field: Mapped[str] = mapped_column(
        Enum("model1_v1", "model1_v2"), nullable=True
    )
    enum_type_field = mapped_column(Enum(EnumChoices), nullable=True)
    choice_field: Mapped[str]
    model2: Mapped["Model2"] = relationship(back_populates="model1")

    def __str__(self):
        return str(self.test1)


class Model2(db.Model):
    __tablename__ = "model2"

    id: Mapped[int] = mapped_column(primary_key=True)
    string_field: Mapped[str]
    string_field_default = mapped_column(TEXT, nullable=False, default="")
    string_field_empty_default = mapped_column(TEXT, nullable=False, default="")
    int_field = mapped_column(Integer)
    bool_field = mapped_column(Boolean)
    enum_field = mapped_column(Enum("model2_v1", "model2_v2"), nullable=True)
    float_field = mapped_column(Float)
    model1_id = mapped_column(ForeignKey("model1.id"))
    model1: Mapped[Model1] = relationship(back_populates="model2")


class Model3(db.Model):
    __tablename__ = "model3"

    id: Mapped[int] = mapped_column(primary_key=True)
    val1: Mapped[str]


class ModelHybrid(db.Model):
    __tablename__ = "model_hybrid"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str]
    width: Mapped[int]
    height: Mapped[int]

    firstname = Mapped[str]
    lastname = Mapped[str]
    tiles: Mapped["ModelHybrid2"] = relationship(back_populates="owner", uselist=True)

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
    __tablename__ = "model_hybrid2"

    id: Mapped[int] = mapped_column(primary_key=True)
    name = Mapped[str]
    owner_id = mapped_column(Integer, ForeignKey("model_hybrid.id", ondelete="CASCADE"))
    owner: Mapped[ModelHybrid] = relationship(back_populates="tiles", uselist=False)


class ModelNoint(db.Model):
    __tablename__ = "model_noint"

    id: Mapped[str] = mapped_column(primary_key=True)
    test = Mapped[str]


class ModelForm(db.Model):
    __tablename__ = "model_form"

    id: Mapped[str] = mapped_column(primary_key=True)
    int_field = mapped_column(Integer)
    datetime_field = mapped_column(DateTime)
    text_field : Mapped[str]
    excluded_column : Mapped[str]
    backref: Mapped["ModelChild"] = relationship(back_populates="model", uselist=False)


class ModelChild(db.Model):
    __tablename__ = "model_child"

    id: Mapped[str] = mapped_column(primary_key=True)
    model_id = mapped_column(Integer, ForeignKey(ModelForm.id))
    model: Mapped[ModelForm] = relationship(back_populates="backref")
    enum_field = mapped_column(Enum("model1_v1", "model1_v2"), nullable=True)
    choice_field = mapped_column(String, nullable=True)
