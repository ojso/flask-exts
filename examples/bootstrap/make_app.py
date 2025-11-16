from flask import Flask
from flask_exts import Exts
from .models import db, Message, MyCategory
from .view import BootstrapView

def create_app():
    app = Flask(__name__)
    app.config["SECRET_KEY"] = "dev"
    init_app(app)
    return app


def init_app(app: Flask):
    exts = Exts()
    exts.init_app(app)
    exts.admin.add_view(BootstrapView())

    with app.app_context():
        db.drop_all()
        db.create_all()

        for i in range(20):
            url = 'mailto:x@t.me'
            if i % 7 == 0:
                url = 'www.t.me'
            elif i % 7 == 1:
                url = 'https://t.me'
            elif i % 7 == 2:
                url = 'http://t.me'
            elif i % 7 == 3:
                url = 'http://t'
            elif i % 7 == 4:
                url = 'http://'
            elif i % 7 == 5:
                url = 'x@t.me'
            m = Message(
                text=f'Message {i+1} {url}',
                author=f'Author {i+1}',
                create_time=4321*(i+1)
                )
            if i % 2:
                m.category = MyCategory.CAT2
            if i % 4:
                m.draft = True
            db.session.add(m)
        db.session.commit()