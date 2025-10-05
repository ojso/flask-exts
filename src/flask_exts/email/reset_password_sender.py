from .smtp import SmtpSSL


class ResetPasswordSender(SmtpSSL):
    def create_emsg(self, data):
        if "subject" not in data:
            data["subject"] = "Please reset your password"
        if "content" not in data:
            data["content"] = data.get("reset_password_link", "")
        if "to" not in data:
            data["to"] = data.get("email")
        return super().create_emsg(data)
