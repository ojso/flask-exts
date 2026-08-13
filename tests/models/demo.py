import enum
from datetime import datetime, date, time
from typing import Optional
from . import db
from . import Mapped
from . import mapped_column
from . import ForeignKey
from . import relationship
from . import hybrid_property
from . import cast
from . import Integer
from . import Boolean
from . import String
from . import TEXT
from . import Enum
from . import Float
from . import DateTime


class EnumChoices(enum.Enum):
    first = 1
    second = 2


class Model1(db.Model):
    __tablename__ = "model1"

    id: Mapped[int] = mapped_column(primary_key=True)
    test1: Mapped[str]
    test2: Mapped[Optional[str]]
    test3: Mapped[Optional[str]] = mapped_column(String(20))
    test4: Mapped[Optional[str]] = mapped_column(TEXT)
    test5 = mapped_column(String(20), nullable=False, default="")
    int_field: Mapped[Optional[int]]
    float_field: Mapped[Optional[float]]
    bool_field: Mapped[Optional[bool]]
    date_field: Mapped[Optional[date]]
    time_field: Mapped[Optional[time]]
    datetime_field: Mapped[Optional[datetime]]
    email_field: Mapped[Optional[str]]
    enum_field: Mapped[Optional[EnumChoices]]
    choice_field: Mapped[Optional[str]]
    model2: Mapped["Model2"] = relationship(back_populates="model1")

    def __str__(self):
        return str(self.test1)


class Model2(db.Model):
    __tablename__ = "model2"

    id: Mapped[int] = mapped_column(primary_key=True)
    string_field: Mapped[str]

    model1_id = mapped_column(ForeignKey("model1.id"))
    model3_id = mapped_column(ForeignKey("model3.id"))

    model1: Mapped[Model1] = relationship(back_populates="model2")
    model3: Mapped["Model3"] = relationship(back_populates="model2")


class Model3(db.Model):
    __tablename__ = "model3"

    id: Mapped[int] = mapped_column(primary_key=True)
    val: Mapped[str]
    model2: Mapped["Model2"] = relationship(back_populates="model3")


class HybridModel(db.Model):
    __tablename__ = "hybrid_model"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str]
    width: Mapped[int]
    height: Mapped[int]

    firstname = Mapped[str]
    lastname = Mapped[str]
    titles: Mapped["HybridModel2"] = relationship(back_populates="owner", uselist=True)

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
        return cast(cls.width * cls.height, String)


class HybridModel2(db.Model):
    __tablename__ = "hybrid_model2"

    id: Mapped[int] = mapped_column(primary_key=True)
    name = Mapped[str]
    owner_id = mapped_column(Integer, ForeignKey("hybrid_model.id", ondelete="CASCADE"))
    owner: Mapped[HybridModel] = relationship(back_populates="titles", uselist=False)


class FormModel(db.Model):
    __tablename__ = "form_model"

    id: Mapped[str] = mapped_column(primary_key=True)
    int_field = mapped_column(Integer)
    datetime_field = mapped_column(DateTime)
    text_field: Mapped[str]
    excluded_column: Mapped[str]
    backref: Mapped["ChildModel"] = relationship(back_populates="model", uselist=False)


class ChildModel(db.Model):
    __tablename__ = "child_model"

    id: Mapped[str] = mapped_column(primary_key=True)
    model_id = mapped_column(Integer, ForeignKey(FormModel.id))
    model: Mapped[FormModel] = relationship(back_populates="backref")
    enum_field = mapped_column(Enum("model1_v1", "model1_v2"), nullable=True)
    choice_field = mapped_column(String, nullable=True)

class StringTestModel(db.Model):
    __tablename__ = "string_test_model"

    id: Mapped[int] = mapped_column(primary_key=True)
    test_no: Mapped[int] = mapped_column(Integer, nullable=False)
    string_field: Mapped[Optional[str]] = mapped_column(String)
    string_field_nonull: Mapped[str] = mapped_column(String, nullable=False)
    string_field_nonull_default: Mapped[str] = mapped_column(
        String, nullable=False, default=""
    )
    text_field: Mapped[Optional[str]] = mapped_column(TEXT)
    text_field_nonull: Mapped[str] = mapped_column(TEXT, nullable=False)
    text_field_nonull_default: Mapped[str] = mapped_column(TEXT, nullable=False, default="")