from ...proxies import current_userstore
from ..exceptions import EmailNotVerifiedError, MissingPasswordError
from ..token_action import TokenBasedAction


class ResetPassword(TokenBasedAction):
    """
    Handles password reset via signed tokens.
    Users receive a reset link via email and can set a new password.
    """

    @property
    def serializer_name(self):
        return "reset_password"

    @property
    def action_type(self):
        return "reset_password"

    @property
    def action_link_endpoint(self):
        return "user.reset_password"

    @property
    def link_url_key(self):
        return "reset_password_link"

    @property
    def token_key(self):
        return "reset_password_token"

    def execute_action(self, user, **kwargs):
        """
        Reset the user's password.

        Args:
            user: The user whose password to reset
            kwargs: Must contain 'password' - the new password

        Returns:
            None after successfully resetting the password.

        Raises:
            EmailNotVerifiedError: If the user's email is not verified.
            MissingPasswordError: If no new password was provided.
        """
        if not user.email_verified:
            raise EmailNotVerifiedError

        password = kwargs.get("password")
        if not password:
            raise MissingPasswordError

        current_userstore.user_set(user, password=user.hash_password(password))
        current_userstore.save_user(user)
