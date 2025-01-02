from abc import ABC, abstractmethod
from flask_login import UserMixin

class User(UserMixin):
    def __init__(self, id, username, password, email):
        self.id = id
        self.username = username
        self.password = password
        self.email = email

    def get_roles(self):
        raise NotImplemented
    
class UserCenter(ABC):
    login_view = "user.login"
    user_class = User

    @abstractmethod
    def user_loader(self, id): ...
