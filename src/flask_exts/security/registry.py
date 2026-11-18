class Registry:
    def __init__(self):
        self._plugins = {}

    def init_all(self, app):
        # email verification
        from .plugins.email_verification import EmailVerification

        email_verification = EmailVerification(app)
        self.register("email_verification", email_verification)

        # email change
        from .plugins.email_change import EmailChange

        email_change = EmailChange(app)
        self.register("email_change", email_change)

        # reset password
        from .plugins.reset_password import ResetPassword

        reset_password = ResetPassword(app)
        self.register("reset_password", reset_password)

        # authorizer
        self.register("authorizer", self._create_authorizer(app))

        # 2FA
        from .plugins.two_factor_authentication import TwoFactorAuthentication

        two_factor_authentication = TwoFactorAuthentication(app)
        self.register("two_factor_authentication", two_factor_authentication)

    def _create_authorizer(self, app):
        """Build the authorizer named by the ``SECURITY_AUTHORIZER`` config.

        Args:
            app: Flask application whose config selects the implementation.

        Returns:
            Authorizer: ``SimpleAuthorizer`` by default, ``RBACAuthorizer`` when
                the config value is ``"rbac"``.

        Raises:
            ValueError: If the configured name is unknown.
        """
        name = app.config.get("SECURITY_AUTHORIZER", "simple")
        if name == "simple":
            from .authorizer.simple_authorizer import SimpleAuthorizer

            return SimpleAuthorizer(app)
        if name == "rbac":
            from .authorizer.rbac_authorizer import RBACAuthorizer

            return RBACAuthorizer(app)
        raise ValueError(
            f"Unknown SECURITY_AUTHORIZER {name!r}; expected 'simple' or 'rbac'."
        )

    def register(self, name, plugin):
        self._plugins[name] = plugin

    def get(self, name: str):
        return self._plugins.get(name)
