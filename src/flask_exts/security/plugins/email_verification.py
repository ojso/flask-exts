from datetime import datetime

from ...proxies import current_userstore
from ..token_action import TokenBasedAction


class EmailVerification(TokenBasedAction):
    """
    Handles email verification via signed tokens.
    Users receive a verification link via email and confirm their email address.
    """

    @property
    def serializer_name(self):
        return "verify_email"

    @property
    def action_type(self):
        return "verify_email"

    @property
    def action_link_endpoint(self):
        return "user.verify_email"

    @property
    def link_url_key(self):
        return "verification_link"

    @property
    def token_key(self):
        return "verification_token"

    def execute_action(self, user, **kwargs):
        """
        Mark the user's email as verified.

        Args:
            user: The user whose email to verify

        Returns:
            A status describing the successful verification outcome.
        """
        if user.email_verified:
            return "already_verified"

        user.email_verified = True
        user.email_verified_at = datetime.now()
        user.is_active = True

        current_userstore.save_user(user)

        return "verified"
