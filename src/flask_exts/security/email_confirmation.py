from datetime import datetime
from flask import url_for
from flask import current_app
from ..proxies import _security
from ..proxies import _usercenter
from ..signals import to_send_email


class EmailConfirmation:
    """
    Class to handle email confirmation functionality.
    This class provides methods to generate confirmation tokens and
    confirm email addresses based on those tokens.
    """

    def __init__(self):
        pass

    def generate_email_confirmation_token(self, user):
        """Generates a confirmation token for the specified user.
        :param user: The user to work with
        """
        data = (str(user.get_identity()), _security.hasher.hash(user.email))
        token = _security.serializer.dumps("confirm", data)
        return token

    def send_email_confirmation_token(self, user):
        """Sends the confirmation instructions email for the specified user.

        :param user: The user to send the instructions to
        """

        token = self.generate_email_confirmation_token(user)
        link = url_for("user.email_confirm", token=token, _external=True)

        email_data = {
            "subject": "email_confirmation",
            "email": user.email,
            "user": user,
            "confirmation_link": link,
            "confirmation_token": token,
        }

        to_send_email.send(current_app._get_current_object(), email_data)

    def confirm_email_token(token, within=None):
        """
        View function which handles an email confirmation request.
        This is always a GET from an email - so for 'spa' must always redirect.
        """
        if within is None:
            within = _security.get_within("confirm")

        expired, invalid, token_data = _security.serializer.loads(
            "confirm", token, within
        )

        if expired:
            return ("expired", None)

        if invalid or not token_data:
            return ("invalid_token", None)

        token_user_identity, token_email_hash = token_data
        user = _usercenter.find_user(token_user_identity)

        if not user:
            return ("no_user", None)

        if not _security.hasher.verify_hash(user.email, token_email_hash):
            return ("invalid_email", None)

        if user.email_verified:
            return ("already_confirmed", user)

        user.email_verified = True
        user.email_verified_at = datetime.now()

        _usercenter.save_user(user)

        return ("confirmed", user)
