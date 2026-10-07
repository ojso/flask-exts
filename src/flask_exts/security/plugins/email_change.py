from datetime import datetime

from flask import current_app, url_for

from ...proxies import current_security, current_userstore
from ...signals import to_send_email
from ...userstore.exceptions import UserAlreadyExistsError
from ..exceptions import (
    ExpiredTokenError,
    InvalidTokenError,
    TokenUserNotFoundError,
)


class EmailChange:
    """Send and validate signed confirmation links for changing an email."""

    serializer_name = "change_email"

    def __init__(self, app=None):
        self.app = app

    def send_token(self, user, new_email):
        if user is None or not user.email or not new_email:
            return

        token_data = (
            str(user.id),
            current_security.hasher.hash(user.email),
            current_security.hasher.hash(user.password or ""),
            new_email,
        )
        token = current_security.serializer.dumps(self.serializer_name, token_data)
        link = url_for(
            "user.confirm_email_change", token=token, _external=True
        )
        to_send_email.send(
            current_app._get_current_object(),
            data={
                "type": "verify_email",
                "email": new_email,
                "verification_link": link,
                "verification_token": token,
                "user": user,
            },
        )

    def execute_with_token(self, token):
        expired, invalid, token_data = current_security.serializer.loads(
            self.serializer_name,
            token,
            current_security.get_within(self.serializer_name),
        )
        if expired:
            raise ExpiredTokenError
        if (
            invalid
            or not isinstance(token_data, (tuple, list))
            or len(token_data) != 4
        ):
            raise InvalidTokenError

        user_id, old_email_hash, password_hash, new_email = token_data
        if not all(
            isinstance(value, str)
            for value in (user_id, old_email_hash, password_hash, new_email)
        ):
            raise InvalidTokenError

        user = current_userstore.get_user_by_identity(user_id)
        if user is None:
            raise TokenUserNotFoundError
        if (
            not current_security.hasher.verify(user.email or "", old_email_hash)
            or not current_security.hasher.verify(
                user.password or "", password_hash
            )
        ):
            raise InvalidTokenError
        if user.email == new_email:
            return "already_verified"

        existing_user = current_userstore.get_user_by_identity(new_email, "email")
        if existing_user is not None and existing_user.id != user.id:
            raise UserAlreadyExistsError("email")

        user.email = new_email
        user.email_verified = True
        user.email_verified_at = datetime.now()
        user.is_active = True
        current_userstore.save_user(user)
        return "verified"
