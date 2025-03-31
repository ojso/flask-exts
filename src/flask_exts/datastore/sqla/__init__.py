from flask_sqlalchemy import SQLAlchemy
from .orm import Base


db = SQLAlchemy(model_class=Base)


def sqldb_init_app(app):
    db.init_app(app)
