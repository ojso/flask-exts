from flask_exts.security.two_factor_authentication import TwoFactorAuthentication


def test_pyotp():
    tfa = TwoFactorAuthentication()
    totp_secret = tfa.generate_totp_secret()
    provisioning_uri = tfa.get_totp_uri(totp_secret, "test@example.com")
    # print("Secret:", totp_secret)
    # print("Provisioning URI:", provisioning_uri)
    assert provisioning_uri.startswith("otpauth://totp/UnknownApp:test%40example.com")

    # verify the TOTP
    totp_now = tfa.get_totp_code(totp_secret)
    # print("Current OTP:", totp_now)

    totp_verify = tfa.verify_totp(totp_secret, totp_now)
    # print("OTP verification result:", totp_verify)
    assert totp_verify is True
