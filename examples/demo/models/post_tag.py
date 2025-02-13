from sqlalchemy import Table
from sqlalchemy import Column
from sqlalchemy import ForeignKey
from . import db

post_tag_table = Table(
    "post_tag",
    db.Model.metadata,
    Column("post_id", ForeignKey("post.id"), primary_key=True),
    Column("tag_id", ForeignKey("tag.id"), primary_key=True),
)
