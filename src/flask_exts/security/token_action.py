from abc import ABC, abstractmethod

from flask import current_app, url_for

from ..proxies import current_security, current_userstore
from ..signals import to_send_email
from .exceptions import (
    ExpiredTokenError,
    InvalidTokenError,
    TokenUserNotFoundError,
)


class TokenBasedAction(ABC):
    """
    Abstract base class that encapsulates common token-based operations:
    token generation, email sending, and token validation/execution.
    Subclasses only need to implement a few methods.
    """

    def __init__(self, app=None):
        self.app = app

    @property
    @abstractmethod
    def serializer_name(self) -> str:
        """Name of the serializer used for this action (e.g., 'verify_email', 'reset_password')."""

    @property
    @abstractmethod
    def action_type(self) -> str:
        """Action type string used in email data's 'type' field."""

    @property
    @abstractmethod
    def action_link_endpoint(self) -> str:
        """Flask endpoint name for the action URL (e.g., 'user.verify_email')."""

    @property
    @abstractmethod
    def link_url_key(self) -> str:
        """Dictionary key name for the verification/reset link in email data."""

    @property
    @abstractmethod
    def token_key(self) -> str:
        """Dictionary key name for the token in email data."""

    def generate_token(self, user):
        """
        Generate a signed token for the given user.

        Args:
            user: The user object

        Returns:
            Signed token string
        """
        data = (
            str(user.id),
            current_security.hasher.hash(user.email),
            current_security.hasher.hash(user.password or ""),
        )
        return current_security.serializer.dumps(self.serializer_name, data)

    def send_token(self, user):
        """
        Send an email containing the action token to the user.

        Args:
            user: The user to send the email to
        """
        if user is None or user.email is None:
            return

        token = self.generate_token(user)
        link = url_for(self.action_link_endpoint, token=token, _external=True)

        data = {
            "type": self.action_type,
            "email": user.email,
            self.link_url_key: link,
            self.token_key: token,
            "user": user,
        }

        to_send_email.send(current_app._get_current_object(), data=data)

    def _load_and_validate_token(self, token, within=None):
        """
        Load and validate the token, returning the associated user if valid.

        Args:
            token: The token string to validate
            within: Optional expiration timeout

        Returns:
            The user associated with the valid token.

        Raises:
            ExpiredTokenError: If the token has expired.
            InvalidTokenError: If the token or its associated email is invalid.
            TokenUserNotFoundError: If the token's user no longer exists.
        """
        if within is None:
            within = current_security.get_within(self.serializer_name)

        expired, invalid, token_data = current_security.serializer.loads(
            self.serializer_name, token, within
        )

        if expired:
            raise ExpiredTokenError

        if invalid or not token_data:
            raise InvalidTokenError

        if len(token_data) != 3:
            raise InvalidTokenError

        token_user_identity, token_email_hash, token_password_hash = token_data
        user = current_userstore.get_user_by_identity(token_user_identity)

        if not user:
            raise TokenUserNotFoundError

        if (
            not current_security.hasher.verify(user.email, token_email_hash)
            or not current_security.hasher.verify(
                user.password or "", token_password_hash
            )
        ):
            raise InvalidTokenError

        return user

    @abstractmethod
    def execute_action(self, user, **kwargs):
        """
        Execute the specific business action after token validation.

        Args:
            user: The validated user object
            kwargs: Additional parameters (e.g., 'password' for reset)

        Returns:
            The action-specific success result.
        """

    def execute_with_token(self, token, within=None, **kwargs):
        """
        Template method: complete token-based workflow.
        1. Validate the token
        2. Execute the specific action (implemented by subclass)

        Args:
            token: The token string
            within: Optional expiration timeout
            kwargs: Additional parameters for the specific action

        Returns:
            The action-specific success result.
        """
        user = self._load_and_validate_token(token, within)
        return self.execute_action(user, **kwargs)
