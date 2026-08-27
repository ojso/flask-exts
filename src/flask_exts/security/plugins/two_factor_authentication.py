import secrets
import string
import pyotp


class TwoFactorAuthentication:
    def __init__(self, app=None):
        self.app = app

    def generate_totp_secret(self):
        return pyotp.random_base32()

    def generate_recovery_codes(self, count=10, length=16):
        alphabet = string.ascii_letters + string.digits
        codes = set()
        while len(codes) < count:
            code = "".join(secrets.choice(alphabet) for _ in range(length))
            codes.add(code)
        return list(codes)

    def get_totp_code(self, otp_secret):
        if otp_secret is None:
            return None
        otp = pyotp.TOTP(otp_secret)
        return otp.now()

    def get_totp_uri(self, otp_secret, username):
        otp = pyotp.TOTP(otp_secret)
        if self.app and self.app.config.get("APP_NAME"):
            app_name = self.app.config.get("APP_NAME")
        else:
            app_name = "UnknownApp"
        uri = otp.provisioning_uri(name=username, issuer_name=app_name)
        return uri

    def verify_totp(self, otp_secret, token):
        otp = pyotp.TOTP(otp_secret)
        return otp.verify(token)
