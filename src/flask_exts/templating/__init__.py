from .bootstrap import Bootstrap
from .csrf import generate_csrf

bootstrap = Bootstrap()


def template_init_app(app):
    app.jinja_env.globals["csrf_token"] = generate_csrf

    if app.config["TEMPLATE_NAME"] == "bootstrap":
        bootstrap.init_app(app)
