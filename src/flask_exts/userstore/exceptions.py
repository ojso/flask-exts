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
