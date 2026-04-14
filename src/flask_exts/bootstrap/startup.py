from .init_flask_login import init_login
from .subscribe import subscribe_signals
from .init_admin_views import add_views
from .init_template import init_jinja


def run_bootstrap(app):
    """Initialize Jinja2, Flask-Login, subscribe to signals and add admin views."""
    init_jinja(app)
    init_login(app)
    subscribe_signals(app)
    add_views(app)
