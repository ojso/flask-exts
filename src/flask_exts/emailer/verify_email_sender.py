from .smtp import SmtpSSL


class VerifyEmailSender(SmtpSSL):
    def create_emsg(self, data):
        if "subject" not in data:
            data["subject"] = "Please verify your email"
        if "content" not in data:
            data["content"] = data.get("verification_link", "")
        if "to" not in data:
            data["to"] = data.get("email")
        return super().create_emsg(data)
