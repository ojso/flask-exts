from ..extension_core.base import Extension
from ..security.core import Security
from ..signals import user_registered


class SecurityExtension(Extension):
    @property
    def name(self) -> str:
        return "security"

    def init_app(self, app):
        self._security = Security()
        self._security.init_app(app)
        self._subscribe_signals(app)

    def get_security(self):
        return self._security

    def _subscribe_signals(self, app):
        @user_registered.connect_via(app)
        def on_user_registered(sender, user, **extra):
            """Send an email-verification token to freshly registered users."""
            if user.email and not user.email_verified:
                self._security.get_plugin("email_verification").send_token(user)
