from . import db
from typing import Optional
from typing import List
from sqlalchemy import ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column
from sqlalchemy import event
from ..file_op import remove_image

class Location(db.Model):
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str]
    images: Mapped[List["LocationImage"]] = relationship(
        "LocationImage", back_populates="location", cascade="all, delete-orphan"
    )


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

    location_id = mapped_column(ForeignKey("location.id"))
    location: Mapped["Location"] = relationship(back_populates="images")

    image_type_id = mapped_column(ForeignKey("image_type.id"))
    image_type: Mapped["ImageType"] = relationship()




# Register after_delete handler which will delete image file after model gets deleted
@event.listens_for(Location, "after_delete")
def _handle_image_delete(mapper, conn, target):
    for location_image in target.images:
        try:
            if location_image.path:
                remove_image(location_image.path)
        except:
            pass