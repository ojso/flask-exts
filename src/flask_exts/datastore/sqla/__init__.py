from .db import Db

db = Db()


def reset_models():
    db.Model.metadata.drop_all(db.engine)
    db.Model.metadata.create_all(db.engine)
