import logging

from flask import current_app

from flask_exts.emailer.base import Emailer
from flask_exts.signals import to_send_email


def test_signal(app):
    recorded = []

    def record(sender, data, **extra):
        recorded.append(data)

    to_send_email.connect(record, app)

    data = {"abc": 123}
    with app.test_request_context():
        to_send_email.send(current_app._get_current_object(), data=data)

    rcd = recorded[0]
    assert rcd == data


def test_missing_sender_warning_redacts_payload(app, caplog):
    emailer = Emailer()
    emailer.app = app
    data = {
        "type": "reset_password",
        "email": "alice@example.com",
        "reset_password_link": "https://example.com/reset?token=secret-token",
        "reset_password_token": "secret-token",
    }

    with caplog.at_level(logging.WARNING):
        assert emailer.send_email("reset_password", data) is None
        emailer.send_email("verify_email", {"type": "verify_email"})

    message = caplog.text
    assert "type=reset_password" in message
    assert "recipient=a***@example.com" in message
    assert "recipient=<unknown>" in message
    assert "alice@example.com" not in message
    assert "secret-token" not in message
    assert "https://example.com" not in message
