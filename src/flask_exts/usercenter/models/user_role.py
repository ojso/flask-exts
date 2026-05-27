from sqlalchemy import Column
from sqlalchemy import Table
from sqlalchemy import ForeignKey
from . import db

user_role_table = Table(
    "user_role",
    db.Model.metadata,
    Column("user_id", ForeignKey("users.id"), primary_key=True),
    Column("role_id", ForeignKey("roles.id"), primary_key=True),
)
