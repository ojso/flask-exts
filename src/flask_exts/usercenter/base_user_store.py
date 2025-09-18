from abc import ABC, abstractmethod


class BaseUserStore(ABC):
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
