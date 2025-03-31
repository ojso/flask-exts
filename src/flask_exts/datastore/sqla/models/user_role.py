from .. import db
from ..orm import Table
from ..orm import ForeignKey
from ..orm import Column

user_role_table = Table(
    "user_role",
    db.Model.metadata,
    Column("user_id", ForeignKey("user.id"), primary_key=True),
    Column("role_id", ForeignKey("role.id"), primary_key=True),
)
