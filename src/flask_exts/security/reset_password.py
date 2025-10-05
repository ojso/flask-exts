from datetime import datetime
from flask import url_for
from flask import current_app
from ..proxies import _security
from ..proxies import _userstore
from ..signals import to_send_email


class ResetPassword:
    """
    Class to handle reset password functionality.
    This class provides methods to generate reset token and reset password with the token.
    """

    def __init__(self, app=None):
        self.app = app
        self.serializer_name = "reset_password"

    def generate_reset_password_token(self, user):
        """Generates a reset password token for the specified user.
        :param user: The user to work with
        """
        data = (str(user.id), _security.hasher.hash(user.email))
        token = _security.serializer.dumps(self.serializer_name, data)
        return token

    def send_reset_password_token(self, user):
        """Sends the reset password token.
        :param user: The user to send the reset password token to.
        """
        if user is None or user.email is None:
            return
        token = self.generate_reset_password_token(user)
        link = url_for("user.reset_password", token=token, _external=True)

        data = {
            "type": "reset_password",
            "email": user.email,
            "reset_password_link": link,
            "reset_password_token": token,
            "user": user,
        }

        to_send_email.send(current_app._get_current_object(), data=data)

    def reset_password_with_token(self, token, password, within=None):
        """
        Resets the password for a user with the given token.
        """
        if within is None:
            within = _security.get_within(self.serializer_name)

        expired, invalid, token_data = _security.serializer.loads(
            self.serializer_name, token, within
        )

        if expired:
            return ("expired", None)

        if invalid or not token_data:
            return ("invalid_token", None)

        token_user_identity, token_email_hash = token_data
        user = _userstore.get_user_by_identity(token_user_identity)

        if not user:
            return ("no_user", None)

        if not _security.hasher.verify(user.email, token_email_hash):
            return ("invalid_token", None)

        if not user.email_verified:
            return ("email_not_verified", None)

        _userstore.user_set(user, password=user.hash_password(password))
        _userstore.save_user(user)

        return ("ok", None)
