from flask_exts.database import db


def reset_models():
    db.drop_all()
    db.create_all()
