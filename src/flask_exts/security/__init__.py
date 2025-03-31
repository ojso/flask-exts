from .core import Security


def security_init_app(app):
    security = Security()
    security.init_app(app)
