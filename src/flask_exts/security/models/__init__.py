from ...datastore.sqla import db

from sqlalchemy import ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column
from sqlalchemy.orm import declared_attr
from sqlalchemy.types import LargeBinary
from sqlalchemy.types import JSON

def init_models():
    pass