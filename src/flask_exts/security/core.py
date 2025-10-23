from flask_login import current_user
from .hasher import Blake2bHasher
from .serializer import TimedUrlSerializer
from .authorizer.casbin_authorizer import CasbinAuthorizer
from .email_verification import EmailVerification
from .reset_password import ResetPassword
from .two_factor_authentication import TwoFactorAuthentication


class Security:
    def __init__(self, app=None):
        self.app = app
        if app is not None:
            self.init_app(app)

    def init_app(self, app):
        self.app = app
        secret_key = app.config.get("SECRET_KEY", "_default_security_secret_key")
        # hasher
        self.hasher = Blake2bHasher(secret_key)
        # serializer
        self.serializer = TimedUrlSerializer(secret_key)
        # email verification
        self.email_verification = EmailVerification(app)
        # reset password
        self.reset_password = ResetPassword(app)
        # authorizer
        self.authorizer = CasbinAuthorizer(app)
        # 2FA
        self.tfa = TwoFactorAuthentication(app)

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
            
        if self.authorizer.is_root_user(user):
            return True
        
        if "role_need" in kwargs:
            if self.authorizer.has_role(user, kwargs["role_need"]):
                return True
        elif "resource" in kwargs and "method" in kwargs:
            if self.authorizer.allow(user, kwargs["resource"], kwargs["method"]):
                return True
            
        return False
