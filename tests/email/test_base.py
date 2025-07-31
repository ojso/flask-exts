from flask import current_app
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
