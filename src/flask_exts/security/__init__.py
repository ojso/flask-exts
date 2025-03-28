from .proxies import _security


def security_init_app(app):
    from .core import Security

    security = Security()
    security.init_app(app)
