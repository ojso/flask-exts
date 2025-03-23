from flask_exts.datastore import db


def reset_models():
    db.drop_all()
    db.create_all()
