from abc import ABC, abstractmethod


class BaseUserCenter(ABC):
    identity_name = "id"
    login_view = "user.login"

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
