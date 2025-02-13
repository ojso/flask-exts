from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy import select


class Base(DeclarativeBase):
    pass


db = SQLAlchemy(model_class=Base)


def init_db(app):
    db.init_app(app)

    from . import user
    from . import keyword
    from . import user_keyword
    from . import tag
    from . import author
    from . import post
    from . import post_tag
    from . import tree
    
