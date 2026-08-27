from flask_login import current_user
from .registry import Registry
from .hasher import Blake2bHasher
from .serializer import TimedUrlSerializer


class Security:
    def __init__(self, app=None):
        self.app = app
        self._registry = Registry()
        if app is not None:
            self.init_app(app)

    def init_app(self, app):
        self.app = app
        secret_key = app.secret_key

        # hasher
        self.hasher = Blake2bHasher(secret_key)

        # serializer
        self.serializer = TimedUrlSerializer(secret_key)

        # registry plugins
        self._registry.load_all(app)

    def get_plugin(self, name):
        return self._registry.get(name)

    def get_within(self, serializer_name):
        """Get the max age for a serializer."""
        return self.app.config.get(
            f"{serializer_name.upper()}_MAX_AGE", 86400 * 7
        )  # default 1 week

    def authorize_allow(self, *args, **kwargs):
        if "user" in kwargs:
            user = kwargs["user"]
        else:
            user = current_user

        authorizer = self.get_plugin("authorizer")

        if authorizer.is_root_user(user):
            return True

        if "role_need" in kwargs:
            if authorizer.has_role(user, kwargs["role_need"]):
                return True
        elif "resource" in kwargs and "method" in kwargs:
            if authorizer.allow(user, kwargs["resource"], kwargs["method"]):
                return True

        return False
