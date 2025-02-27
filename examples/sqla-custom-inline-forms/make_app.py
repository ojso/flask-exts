import os.path as op
import os
from sqlalchemy import event
from flask import Flask
from flask import send_file
from flask_exts import Manager
from flask_exts.admin.menu import MenuLink
from .models import db

from .views.image_view import locationview
# from .views.my_view import myview
# from .views.user_view import userview
# from .views.tree_view import treeview
# from .views.post_view import authorview
# from .views.post_view import tagview

# Figure out base upload path
static_path = op.join(op.dirname(__file__), 'static')

def remove_image(image_path):
    os.remove(op.join(static_path, image_path))

def save_image(file_data,image_path):
    file_data.save(op.join(static_path, image_path))

def get_sqlite_path():
    app_dir = op.realpath(op.dirname(__file__))
    database_path = op.join(app_dir, "sample.sqlite")
    return database_path

def create_app():
    app = Flask(__name__)
    app.config["SECRET_KEY"] = "dev"

    # app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///:memory:"
    # app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite://'
    # app.config['SQLALCHEMY_ECHO'] = True
    app.config["DATABASE_FILE"] = get_sqlite_path()
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///" + app.config["DATABASE_FILE"]
    init_app(app)

    return app


def init_app(app: Flask):
    app.save_image = save_image

    from .models.model import Location

    # Register after_delete handler which will delete image file after model gets deleted
    @event.listens_for(Location, 'after_delete')
    def _handle_image_delete(mapper, conn, target):
        for location_image in target.images:
            try:
                if location_image.path:
                    remove_image(location_image.path)
            except:
                pass

    manager = Manager()
    manager.init_app(app)

    admin = app.extensions["admin"][0]

    admin.add_view(locationview)
    admin.menu.add_link(MenuLink(name='locationlist', url='/locationlist', category='List'))

    @app.route('/locationlist')
    def location_list():
        from .models.model import Location
        from flask import render_template
        locations = db.session.query(Location).all()
        return render_template('locations.html', locations=locations)

    if not op.exists(app.config["DATABASE_FILE"]):
        with app.app_context():            
            from .data import build_sample_db
            build_sample_db()
