import os.path as op
from flask import Flask
from flask_exts import Exts


def get_sqlite_path():
    app_dir = op.realpath(op.dirname(__file__))
    database_path = op.join(app_dir, "sample.sqlite")
    return database_path


def create_app():
    app = Flask(__name__, instance_relative_config=True)
    app.config["SECRET_KEY"] = "dev"
    app.config.from_pyfile('config.py',silent=True)
    app.config.from_pyfile('config_prod.py',silent=True)
    # app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///:memory:"
    # app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite://'
    # app.config["SQLALCHEMY_ECHO"] = True
    app.config["DATABASE_FILE"] = get_sqlite_path()
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///" + app.config["DATABASE_FILE"]
    app.config["ADMIN_ALL_ACCESSED"] = False
    init_app(app)
    return app


def init_app(app: Flask):
    exts = Exts()
    exts.init_app(app)

    from .models import init_models

    init_models()

    from .admin_views import add_views

    add_views(app)

    @app.route("/locationlist")
    def location_list():
        from .models.location_image import Location
        from flask import render_template
        from .models import db

        locations = db.session.query(Location).all()
        return render_template("locations.html", locations=locations)

    if not op.exists(app.config["DATABASE_FILE"]):
        with app.app_context():
            from .build_sample import build_sample_db

            build_sample_db()
