from blinker import Namespace

_signals = Namespace()

to_send_email = _signals.signal("send-email")

user_registered = _signals.signal("user-registered")
