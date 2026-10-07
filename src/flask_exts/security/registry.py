class Registry:
    def __init__(self):
        self._plugins = {}

    def init_all(self,app):
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
        from .authorizer.simple_authorizer import SimpleAuthorizer

        simple_authorizer = SimpleAuthorizer(app)
        self.register("authorizer", simple_authorizer)

        # 2FA
        from .plugins.two_factor_authentication import TwoFactorAuthentication

        two_factor_authentication = TwoFactorAuthentication(app)
        self.register("two_factor_authentication", two_factor_authentication)

    def register(self, name, plugin):
        self._plugins[name] = plugin

    def get(self, name: str):
        return self._plugins.get(name)
