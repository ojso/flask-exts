from abc import ABC, abstractmethod
from ..signals import user_registered
from ..proxies import _security


class BaseUserCenter(ABC):
    identity_name = "id"

    @abstractmethod
    def user_loader(self, id): ...

    @abstractmethod
    def create_user(self, **kwargs): ...

    @abstractmethod
    def get_users(self, **kwargs): ...

    @abstractmethod
    def get_user_by_id(self, id): ...

    @abstractmethod
    def get_user_by_identity(self, identity_id, identity_name=None): ...

    @abstractmethod
    def get_user_identity(self, user): ...

    @abstractmethod
    def user_set(self, user, **kwargs): ...

    @abstractmethod
    def save_user(self, user): ...

    def init_app(self, app):
        self.app = app
        self.subscribe_signal(app)

    def subscribe_signal(self, app):
        user_registered.connect(self.after_user_registered, app)

    def after_user_registered(self, sender, user, **kwargs):
        """Signal handler for user registration."""
        if user.email and not user.email_verified:
            _security.email_verification.send_verify_email_token(user)
