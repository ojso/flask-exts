from abc import ABC, abstractmethod
from flask import url_for, current_app
from ..proxies import current_security, current_userstore
from ..signals import to_send_email


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
        pass

    @property
    @abstractmethod
    def action_type(self) -> str:
        """Action type string used in email data's 'type' field."""
        pass

    @property
    @abstractmethod
    def action_link_endpoint(self) -> str:
        """Flask endpoint name for the action URL (e.g., 'user.verify_email')."""
        pass

    @property
    @abstractmethod
    def link_url_key(self) -> str:
        """Dictionary key name for the verification/reset link in email data."""
        pass

    @property
    @abstractmethod
    def token_key(self) -> str:
        """Dictionary key name for the token in email data."""
        pass

    def generate_token(self, user):
        """
        Generate a signed token for the given user.

        :param user: The user object
        :return: Signed token string
        """
        data = (str(user.id), current_security.hasher.hash(user.email))
        return current_security.serializer.dumps(self.serializer_name, data)

    def send_token(self, user):
        """
        Send an email containing the action token to the user.

        :param user: The user to send the email to
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

        :param token: The token string to validate
        :param within: Optional expiration timeout
        :return: (user_or_None, error_tuple_or_None)
                 error_tuple is (status_code, additional_data)
        """
        if within is None:
            within = current_security.get_within(self.serializer_name)

        expired, invalid, token_data = current_security.serializer.loads(
            self.serializer_name, token, within
        )

        if expired:
            return None, ("expired", None)

        if invalid or not token_data:
            return None, ("invalid_token", None)

        token_user_identity, token_email_hash = token_data
        user = current_userstore.get_user_by_identity(token_user_identity)

        if not user:
            return None, ("no_user", None)

        if not current_security.hasher.verify(user.email, token_email_hash):
            return None, ("invalid_token2", None)

        return user, None

    @abstractmethod
    def execute_action(self, user, **kwargs):
        """
        Execute the specific business action after token validation.

        :param user: The validated user object
        :param kwargs: Additional parameters (e.g., 'password' for reset)
        :return: (status_code, result_data) tuple
        """
        pass

    def execute_with_token(self, token, within=None, **kwargs):
        """
        Template method: complete token-based workflow.
        1. Validate the token
        2. Execute the specific action (implemented by subclass)

        :param token: The token string
        :param within: Optional expiration timeout
        :param kwargs: Additional parameters for the specific action
        :return: (status_code, result_data) tuple
        """
        user, error = self._load_and_validate_token(token, within)
        if error:
            return error

        return self.execute_action(user, **kwargs)
