from datetime import datetime


class UserStoreError(Exception):
    """Base class for expected user-store errors."""


class UserAlreadyExistsError(UserStoreError):
    def __init__(self, field: str):
        self.field = field
        super().__init__(f"{field} already exists")


class InvalidCredentialsError(UserStoreError):
    field = "username"

    def __init__(self):
        super().__init__("Invalid username or password.")


class AccountLockedError(UserStoreError):
    """Raised when a failed-login lockout is still in effect."""

    field = "username"

    def __init__(self, locked_until: datetime, now: datetime | None = None):
        self.locked_until = locked_until
        remaining = (locked_until - (now or datetime.now())).total_seconds()
        self.retry_after = max(int(remaining), 0)
        super().__init__(
            "Too many failed sign-in attempts. "
            f"Try again in {self._format_retry_after()}."
        )

    def _format_retry_after(self) -> str:
        if self.retry_after < 60:
            return f"{self.retry_after} seconds"
        minutes = (self.retry_after + 59) // 60
        if minutes < 60:
            return f"{minutes} minutes"
        hours = (minutes + 59) // 60
        return f"{hours} hours"
