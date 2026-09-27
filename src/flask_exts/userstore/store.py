from __future__ import annotations

from abc import ABC, abstractmethod


class UserStore(ABC):
    """Abstract storage contract for user-related persistence operations.

    This base class defines the interface used by the user-facing application
    layer. Concrete implementations, such as SQLAlchemy-backed stores, provide
    the database behavior behind the contract.
    """

    identity_name = "id"

    @abstractmethod
    def user_loader(self, id):
        """Return a user by primary key."""

    @abstractmethod
    def create_user(self, **kwargs):
        """Create a user with the provided attributes."""

    @abstractmethod
    def get_users(self, **kwargs):
        """Return a collection of users matching the provided filters."""

    @abstractmethod
    def get_user_by_id(self, id):
        """Return a user by database identifier."""

    @abstractmethod
    def get_user_by_identity(self, identity_id, identity_name=None):
        """Return a user by a named identity attribute."""

    @abstractmethod
    def get_user_identity(self, user):
        """Return the identity value for a user."""

    @abstractmethod
    def user_set(self, user, **kwargs):
        """Apply user attribute updates."""

    @abstractmethod
    def save_user(self, user):
        """Persist a user instance to the backing store."""

    @abstractmethod
    def create_role(self, name):
        """Create a user role with the given name."""
