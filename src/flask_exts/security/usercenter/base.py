from abc import ABC, abstractmethod
from ..forms import LoginForm
from ..forms import RegisterForm


class BaseUserCenter(ABC):
    login_view = "user.login"
    login_form_class = LoginForm
    register_form_class = RegisterForm

    @abstractmethod
    def user_loader(self, id): ...

    @abstractmethod
    def create_user(self, **kwargs): ...

    @abstractmethod
    def get_user_by_id(self, id): ...

    @abstractmethod
    def get_user_by_uniquifier(self, uniquifier): ...
