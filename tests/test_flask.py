import pytest
from flask import current_app
from blinker import Namespace

_signals = Namespace()
my_signal = _signals.signal("my-signal")


def my_signal_handler(sender, data):
    # print(f"id(sender): {id(sender)},data:{data}")
    assert id(sender) == int(data)


def test_app_id(app, client):
    app_id = f"{id(app)}"
    # print(f"App ID: {app_id}")

    # Test accessing current_app
    @app.route("/test_app_id")
    def app_id_view():
        current_app_id = id(current_app._get_current_object())
        # print(f"Current App ID: {current_app_id}")
        return f"{current_app_id}"

    rv = client.get("/test_app_id")
    assert rv.status_code == 200
    assert rv.text == app_id

    # Test signal sending
    my_signal.connect(my_signal_handler, app)

    with app.app_context():
        my_signal.send(
            current_app._get_current_object(),
            data=app_id,
        )
