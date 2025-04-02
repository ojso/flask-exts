from abc import ABC, abstractmethod


class BaseAuthorizer(ABC):
    @abstractmethod
    def allow(self, user, *source): ...


class Watcher(ABC):
    """
    Watcher interface as it should be implemented for flask-casbin
    """

    @abstractmethod
    def update(self):
        """
        Watcher interface as it should be implemented for flask-casbin
        Returns:
            None
        """
        pass

    @abstractmethod
    def set_update_callback(self):
        """
        Set the update callback to be used when an update is detected
        Returns:
            None
        """
        pass

    @abstractmethod
    def should_reload(self):
        """
        Method which checks if there is an update necessary for the casbin
        roles. This is called with each flask request.
        Returns:
            Bool
        """
        pass
