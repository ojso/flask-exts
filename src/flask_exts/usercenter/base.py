from abc import ABC, abstractmethod


class BaseUserCenter(ABC):
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
    def get_user_by_uuid(self, uuid): ...
