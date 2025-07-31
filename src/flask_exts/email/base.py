from ..signals import to_send_email


class Email:
    def __init__(self, app=None):
        self.app = None
        if app is not None:
            self.init_app(app)

    def init_app(self, app):
        self.app = app
        self.subscript_signal(app)

    def subscript_signal(self, app):
        to_send_email.connect(self.send, app)

    def send(self, sender, data, **extra):
        # todo send email with data
        print(data)
