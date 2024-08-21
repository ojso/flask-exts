from flask_sqlalchemy import SQLAlchemy
from typing import Optional
from typing import List
from sqlalchemy.types import String
from sqlalchemy.types import Integer
from sqlalchemy.types import JSON
from sqlalchemy.sql.expression import func
from sqlalchemy.sql.expression import or_
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column
from sqlalchemy.orm import relationship
from sqlalchemy.orm import declared_attr
from sqlalchemy import select
from sqlalchemy import ForeignKey
from sqlalchemy import UniqueConstraint
from sqlalchemy import Column
from sqlalchemy import Table


db = SQLAlchemy()


def init_db(app):
    db.init_app(app)
