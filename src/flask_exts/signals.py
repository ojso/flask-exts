from blinker import Namespace

_signals = Namespace()

to_send_email = _signals.signal("to-send-email")

user_registered = _signals.signal("user-registered")
