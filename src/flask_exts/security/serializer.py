import typing as t
from itsdangerous import URLSafeTimedSerializer
from itsdangerous import BadSignature, SignatureExpired


class TimedUrlSerializer:
    """Timed serializer for creating and verifying tokens with expiration."""

    def __init__(self, key):
        self.key = key

    def dumps(self, serializer_name: str, data) -> str:
        """Create a token with the given serializer name and data.
        :param serializer_name: The name of the serializer. Can be one of the
                                following: ``confirm``, ``login``, ``reset``, ``us_setup`
                                ``remember``, ``two_factor_validity``, ``wan``
        :param data: The data to serialize into the token
        :return: A URL-safe token string
        """
        s = URLSafeTimedSerializer(self.key, salt=serializer_name)
        token = s.dumps(data)
        return token

    def loads(
        self, serializer_name: str, token: str, max_age: int | None = 259200  # 3 days
    ) -> tuple[bool, bool, t.Any]:
        """Get the status of a token and return data.

        :param token: The token to check
        :param serializer_name: The name of the serializer. Can be one of the
                        following: ``confirm``, ``login``, ``reset``, ``us_setup``
                        ``remember``, ``two_factor_validity``, ``wan``
        :param max_age: The maximum age of the token in seconds. If None, no max age is enforced.

        :return: a tuple of (expired, invalid, data)

        """
        s = URLSafeTimedSerializer(self.key, salt=serializer_name)
        data = None
        expired, invalid = False, False

        try:
            data = s.loads(token, max_age=max_age)
        except SignatureExpired:
            # _, data = s.loads_unsafe(token)
            expired = True
        except (BadSignature, TypeError, ValueError):
            invalid = True

        return expired, invalid, data
