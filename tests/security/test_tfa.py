import pyotp


def test_pyotp():
    totp_secret = pyotp.random_base32()
    totp = pyotp.TOTP(totp_secret)

    provisioning_uri = totp.provisioning_uri(
        name="user@example.com", issuer_name="MyApp"
    )
    # print("Secret:", totp_secret)
    # print("Provisioning URI:", provisioning_uri)
    assert provisioning_uri.startswith("otpauth://totp/MyApp:user%40example.com")

    totp_now = totp.now()
    # print("Current OTP:", totp_now)

    totp_verify = totp.verify(totp_now)
    # print("OTP verification result:", totp_verify)
    assert totp_verify is True
