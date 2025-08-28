from ..signals import to_send_email
from .verify_email_sender import VerifyEmailSender

class Email:
    def __init__(self, app=None):
        self.app = None
        self.senders = {}
        if app is not None:
            self.init_app(app)

    def init_app(self, app):
        self.app = app
        self.subscribe_signal(app)

    def subscribe_signal(self, app):
        to_send_email.connect(self.send, app)

    def send(self, sender, data, **extra):
        if "type" not in data:
            self.app.logger.warning("Email data must contain a 'type' field.")
            return
        self.send_email(data["type"], data)

    def register_sender(self, name, sender):
        """Register a sender with a name."""
        if name in self.senders:
            raise ValueError(f"Sender with name {name} already exists.")
        self.senders[name] = sender

    def send_email(self, name, data):
        """Send an email using a registered sender."""
        if name not in self.senders:
            self.app.logger.warning(f"Email can not send data: {data}, because it can not find the sender: {name}")
            # raise ValueError(f"Email can not find the sender: {name}")
            return
        sender = self.senders.get(name)
        return sender.send(data)
    
    def register_senders(self):
        """Register multiple senders."""
        if "VERIFY_EMAIL_SENDER" in self.app.config:
            verify_email_sender = VerifyEmailSender(**self.app.config["VERIFY_EMAIL_SENDER"])
            self.register_sender("verify_email", verify_email_sender)
