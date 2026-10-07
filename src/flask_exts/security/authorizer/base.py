from abc import ABC, abstractmethod

SESSION_KEY_TFA_VERIFIED = "tfa_verified"


class Authorizer(ABC):
    @abstractmethod
    def allow(self, *args, **kwargs): ...
