import typing as t
from datetime import timedelta
from itsdangerous import URLSafeTimedSerializer
from itsdangerous import BadSignature, SignatureExpired
from ..utils.hasher import Blake2bHasher

class Security:
    def __init__(
        self,
        app=None,
    ):
        self.app = app
        if app is not None:
            self.init_app(app)

    def get_serializer(self, salt):
        secret_key = self.app.config.get("SECRET_KEY")
        return URLSafeTimedSerializer(secret_key, salt=salt)

    def init_app(
        self,
        app,
    ):
        self.app = app

        # hasher
        self.hasher = Blake2bHasher(app.config.get("SECRET_KEY"))
        
        # serializer
        self.remember_token_serializer = self.get_serializer("remember")
        self.login_serializer = self.get_serializer("login")
        self.reset_serializer = self.get_serializer("reset")
        self.change_email_serializer = self.get_serializer("change_email")
        self.confirm_serializer = self.get_serializer("confirm")
        self.us_setup_serializer = self.get_serializer("us_setup")
        self.tf_setup_serializer = self.get_serializer("two_factor_setup")
        self.tf_validity_serializer = self.get_serializer("two_factor_validity")
        self.wan_serializer = self.get_serializer("wan")

    def check_and_get_token_status(
        self, token: str, serializer_name: str, within: timedelta
    ) -> tuple[bool, bool, t.Any]:
        """Get the status of a token and return data.

        :param token: The token to check
        :param serializer_name: The name of the serializer.
        :param within: max age - passed as a timedelta

        :return: a tuple of (expired, invalid, data)
        """
        serializer = getattr(self, serializer_name + "_serializer")
        max_age = within.total_seconds()
        expired, invalid, data = False, False, None

        try:
            data = serializer.loads(token, max_age=max_age)
        except SignatureExpired:
            d, data = serializer.loads_unsafe(token)
            expired = True
        except (BadSignature, TypeError, ValueError):
            invalid = True

        return expired, invalid, data


