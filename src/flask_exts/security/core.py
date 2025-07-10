from .hasher import Blake2bHasher
from .serializer import TimedUrlSerializer
from .authorizer.casbin_authorizer import CasbinAuthorizer

class Security:
    def __init__(
        self,
        app=None,
    ):
        self.app = app
        if app is not None:
            self.init_app(app)

    def init_app(
        self,
        app,
    ):
        self.app = app

        secret_key = app.config.get("SECRET_KEY")

        # hasher
        self.hasher = Blake2bHasher(secret_key)

        # serializer
        self.serializer = TimedUrlSerializer(secret_key)

        # authorizer
        self.authorizer = CasbinAuthorizer(app)

    def get_within(self, serializer_name):
        """Get the max age for a serializer."""
        return self.app.config.get(f"{serializer_name.upper()}_MAX_AGE", None)

