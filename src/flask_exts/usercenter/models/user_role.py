from ...datastore.sqla import db
from ...datastore.sqla.orm import ForeignKey
from ...datastore.sqla.orm import Table
from ...datastore.sqla.orm import Column

user_role_table = Table(
    "user_role",
    db.Model.metadata,
    Column("user_id", ForeignKey("users.id"), primary_key=True),
    Column("role_id", ForeignKey("roles.id"), primary_key=True),
)
