import os.path
from flask import Flask
from flask import send_file
from flask_exts import Manager
from .models import db
from .user_center import UserCenter
from .views.my_view import myview
from .views.user_view import userview
from .views.tree_view import treeview
from .views.post_view import authorview
from .views.post_view import tagview
# from .views.post_view import postview
from flask_exts.admin.menu import MenuLink


def get_sqlite_path():
    app_dir = os.path.realpath(os.path.dirname(__file__))
    database_path = os.path.join(app_dir, "sample.sqlite")
    return database_path


def register_users(app):
    user_center = app.config["USER_CENTER"]
    user_center.register_user("admin", "admin", "admin@example.com")


def create_app():
    app = Flask(__name__)
    app.config["SECRET_KEY"] = "dev"

    # app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///:memory:"
    # app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite://'
    # app.config['SQLALCHEMY_ECHO'] = True
    app.config["DATABASE_FILE"] = get_sqlite_path()
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///" + app.config["DATABASE_FILE"]

    app.config["USER_CENTER"] = UserCenter()

    init_app(app)

    return app


def init_app(app: Flask):

    @app.route('/favicon.ico')
    def favicon():
        return send_file('static/favicon.ico')

    from .models import init_db

    init_db(app)

    manager = Manager()
    manager.init_app(app)

    admin = app.extensions["admin"][0]

    admin.add_view(myview)
    admin.add_view(userview)
    admin.add_view(treeview)
    admin.add_view(authorview)
    admin.add_view(tagview)
    # admin.add_view(postview)
    admin.add_link(MenuLink(name='other', url='/', category='other'))
    admin.add_sub_category(name="Links", parent_name="Other")
    admin.add_link(MenuLink(name='Back Home', url='/', category='Links'))
    admin.add_link(MenuLink(name='External link', url='http://www.example.com/', category='Links'))

    if not os.path.exists(app.config["DATABASE_FILE"]):
        with app.app_context():            
            from .data import build_sample_db
            build_sample_db()
            register_users(app)

