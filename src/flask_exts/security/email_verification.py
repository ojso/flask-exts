from datetime import datetime
from flask import url_for
from flask import current_app
from ..proxies import _security
from ..proxies import _userstore
from ..signals import to_send_email


class EmailVerification:
    """
    Class to handle verify email functionality.
    This class provides methods to generate verify tokens and
    email addresses based on those tokens.
    """

    def __init__(self, app=None):
        self.app = app
        self.serializer_name = "verify_email"

    def generate_verify_email_token(self, user):
        """Generates a verification token for the specified user.
        :param user: The user to work with
        """
        data = (str(user.id), _security.hasher.hash(user.email))
        token = _security.serializer.dumps(self.serializer_name, data)
        return token

    def send_verify_email_token(self, user):
        """Sends the verify instructions email for the specified user.

        :param user: The user to send the instructions to
        """
        if user is None or user.email is None:
            return
        token = self.generate_verify_email_token(user)
        link = url_for("user.verify_email", token=token, _external=True)

        data = {
            "type": "verify_email",
            "email": user.email,
            "verification_link": link,
            "verification_token": token,
            "user": user,
        }

        to_send_email.send(current_app._get_current_object(), data=data)

    def verify_email_with_token(self, token, within=None):
        """
        View function which handles an email verification request.
        This is always a GET from an email - so for 'spa' must always redirect.
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
            return ("invalid_email", None)

        if user.email_verified:
            return ("already_verified", user)

        user.email_verified = True
        user.email_verified_at = datetime.now()
        user.actived = True

        _userstore.save_user(user)

        return ("verified", user)
