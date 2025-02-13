from .models import db
from .models.model import ImageType

def build_sample_image_type():

    # Add some image types for the form_ajax_refs inside the inline_model
    image_types = ("JPEG", "PNG", "GIF")
    for image_type in image_types:
        itype = ImageType(name=image_type)
        db.session.add(itype)
    db.session.commit()


def build_sample_db():
    """
    Populate a small db with some example entries.
    """

    db.drop_all()
    db.create_all()

    build_sample_image_type()

