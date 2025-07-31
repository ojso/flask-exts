import pytest
from flask import current_app

from blinker import Namespace

_signals = Namespace()

print_signal = _signals.signal("print-signal")

def my_signal(sender, data):
    # print(f"id(sender): {id(sender)},data:{data}")
    pass

def test_app_id(app,client):
    app_id = f"{id(app)}"
    # print(f"App ID: {app_id}")
    @app.route('/test_app_id')
    def app_id_view():
        current_app_id = id(current_app._get_current_object())
        # print(f"Current App ID: {id_app}")
        return f"{current_app_id}"

    rv = client.get('/test_app_id')
    assert rv.status_code == 200
    assert rv.text == app_id


def test_signal(app):
    print_signal.connect(my_signal,app)
    with app.app_context():
        print_signal.send(
            current_app._get_current_object(),
            data="test_signal",
        )