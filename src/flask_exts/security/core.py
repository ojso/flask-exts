class Security:
    def __init__(self, app=None):
        self.app = app
        if app is not None:
            self.init_app(app)

    def init_app(self, app):
        self.app = app
        secret_key = app.secret_key

        from .hasher import Blake2bHasher
        from .keys import derive_key
        from .registry import Registry
        from .serializer import TimedUrlSerializer

        self._registry = Registry()

        # hasher
        self.hasher = Blake2bHasher(derive_key(secret_key, "hasher"))

        # serializer
        self.serializer = TimedUrlSerializer(derive_key(secret_key, "url-token"))

        # registry plugins
        self._registry.init_all(app)

    def get_plugin(self, name):
        return self._registry.get(name)

    def get_within(self, serializer_name):
        """Get the max age for a serializer."""
        default_max_age = 1800 if serializer_name == "reset_password" else 86400 * 7
        return self.app.config.get(
            f"{serializer_name.upper()}_MAX_AGE", default_max_age
        )

    def authorize_allow(self, *args, **kwargs):
        authorizer = self.get_plugin("authorizer")
        return authorizer.authorize(*args, **kwargs)
