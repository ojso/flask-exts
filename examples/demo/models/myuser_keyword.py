from sqlalchemy import ForeignKey
from sqlalchemy import Table, Column, Integer, String
from . import db


myuser_keyword_table = Table(
    "myuser_keyword_table",
    db.Model.metadata,
    Column("myuser_id", Integer, ForeignKey("myuser.id"), primary_key=True),
    Column("keyword_id", Integer, ForeignKey("keyword.id"), primary_key=True),
    Column("special_key", String(255), nullable=True),
)
