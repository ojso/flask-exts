from flask import session
from flask_login import user_logged_out
from ..signals import user_registered
from ..proxies import _security


def subscribe_signals(app):
    subscribe_signal_user_logged_out(app)
    subscribe_signal_user_registered(app)


def subscribe_signal_user_logged_out(app):
    @user_logged_out.connect_via(app)
    def on_user_logged_out(sender, user, **extra):
        if "tfa_verified" in session:
            session.pop("tfa_verified")


def subscribe_signal_user_registered(app):
    @user_registered.connect_via(app)
    def on_user_registered(sender, user, **extra):
        """Signal handler for user registration."""
        if user.email and not user.email_verified:
            _security.email_verification.send_verify_email_token(user)
