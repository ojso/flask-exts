_DEFAULT_MAX_AGES = {
    "reset_password": 1800,
    "verify_email": 86400 * 7,
    "change_email": 86400 * 7,
}
_FALLBACK_MAX_AGE = 1800


class Security:
    def __init__(self, app=None):
        self.app = app
        if app is not None:
            self.init_app(app)

    def init_app(self, app):
        self.app = app
        secret_key = app.secret_key
        if not secret_key:
            raise RuntimeError(
                "SECRET_KEY must be configured before Security.init_app(); "
                "security keys are derived once during initialization."
            )

        from .encryptor import AesGcmEncryptor
        from .hasher import Blake2bHasher
        from .keys import derive_key
        from .registry import Registry
        from .serializer import TimedUrlSerializer

        self._registry = Registry()

        # hasher
        self.hasher = Blake2bHasher(derive_key(secret_key, "hasher"))

        # serializer
        self.serializer = TimedUrlSerializer(derive_key(secret_key, "url-token"))

        # encryptor: for secrets that must be decrypted back to plaintext
        # (e.g. TOTP seeds), unlike hasher which is one-way.
        self.encryptor = AesGcmEncryptor(derive_key(secret_key, "encryptor"))

        # registry plugins
        self._registry.init_all(app)

    def get_plugin(self, name):
        return self._registry.get(name)

    def get_within(self, serializer_name):
        """Get the max age for a serializer."""
        default_max_age = _DEFAULT_MAX_AGES.get(serializer_name, _FALLBACK_MAX_AGE)
        return self.app.config.get(
            f"{serializer_name.upper()}_MAX_AGE", default_max_age
        )

    def authorize_allow(self, *args, **kwargs):
        authorizer = self.get_plugin("authorizer")
        return authorizer.authorize(*args, **kwargs)

    def authorize_object(self, view, fn, obj, requirement):
        """Authorize a single object for an exposed admin view method.

        Args:
            view: The admin view instance owning the object.
            fn: The exposed view method being called.
            obj: The object the request resolved to.
            requirement: Object-level requirement to evaluate.

        Returns:
            bool: ``True`` when the object is allowed.
        """
        authorizer = self.get_plugin("authorizer")
        return authorizer.authorize_object(view, fn, obj, requirement)
