import smtplib
from email.message import EmailMessage
from .sender import Sender


class SmtpSSL(Sender):
    def __init__(self, host, port, user, password):
        self.host = host
        self.port = port
        self.user = user
        self.password = password

    def create_emsg(self, data):
        emsg = EmailMessage()
        emsg["Subject"] = data["subject"]
        emsg.set_content(data["content"])

        if data.get("From") is None:
            emsg["From"] = self.user

        emsg["To"] = data["to"]

        if "cc" in data:
            emsg["Cc"] = data["cc"]

        if "bcc" in data:
            emsg["Bcc"] = data["bcc"]

        return emsg

    def send(self, data):
        emsg = self.create_emsg(data)
        try:
            with smtplib.SMTP_SSL(self.host, self.port) as smtp:
                # smtp.set_debuglevel(1)
                smtp.login(self.user, self.password)
                senderrs = smtp.send_message(emsg)
                return senderrs
        except Exception as e:
            # print(f"Error sending email: {e}")
            return str(e)
