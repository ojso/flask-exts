from flask_exts.datastore.sqla import db

from .author import Author
from .post import Post
from .post_tag import post_tag_table
from .tag import Tag
from .tree import Tree
from .user_interest import UserInterest

__all__ = [
    "Author",
    "Post",
    "Tag",
    "Tree",
    "UserInterest",
    "db",
    "post_tag_table",
]
