from . import db
from typing import Optional
from sqlalchemy import ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column


class Location(db.Model):
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str]


class ImageType(db.Model):
    """
    Just so the LocationImage can have another foreign key,
    so we can test the "form_ajax_refs" inside the "inline_models"
    """

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str]

    def __repr__(self) -> str:
        """
        Represent this model as a string
        (e.g. in the Image Type list dropdown when creating an inline model)
        """
        return self.name


class LocationImage(db.Model):
    id: Mapped[int] = mapped_column(primary_key=True)
    alt: Mapped[str]
    path: Mapped[str]

    location_id: Mapped[int] = mapped_column(ForeignKey("location.id"))
    location: Mapped["Location"] = relationship(backref='images')

    image_type_id: Mapped[int] = mapped_column(ForeignKey("image_type.id"))
    image_type: Mapped["ImageType"] = relationship(backref='images')


