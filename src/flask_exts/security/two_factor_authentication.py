import pyotp


class TwoFactorAuthentication:
    def __init__(self, app):
        self.app = app

    def generate_totp_secret(self):
        return pyotp.random_base32()

    def get_totp_uri(self, otp_secret, username):
        otp = pyotp.totp.TOTP(otp_secret)
        uri = otp.provisioning_uri(
            name=username, issuer_name=self.app.config.get("APP_NAME", "Unknown App")
        )
        return uri
