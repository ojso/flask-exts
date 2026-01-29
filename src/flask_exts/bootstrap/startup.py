from .init_flask_login import init_login
from .subscribe import subscribe_signals
from .init_admin_views import add_views

def run_bootstrap(app):
    """Initialize Flask-Login and subscribe to signals."""
    init_login(app)
    subscribe_signals(app)
    add_views(app)
