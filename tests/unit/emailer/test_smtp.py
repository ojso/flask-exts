import ssl

import pytest

from flask_exts.emailer import smtp as smtp_module
from flask_exts.emailer.smtp import SmtpError, SmtpSSL

MESSAGE = {
    "to": "davidhua@foxmail.com",
    "subject": "This is a test subject.",
    "content": "This is a test email.",
}


def test_smtp_ssl_sends_over_a_verified_context(monkeypatch):
    captured = {}

    class FakeSMTP:
        def __init__(self, host, port, timeout=None, context=None):
            captured["host"] = host
            captured["port"] = port
            captured["context"] = context

        def __enter__(self):
            return self

        def __exit__(self, *exc_info):
            return False

        def login(self, user, password):
            captured["login"] = (user, password)

        def send_message(self, emsg):
            captured["message"] = emsg
            return {"someone@example.com": (550, b"no such user")}

    monkeypatch.setattr(smtp_module.smtplib, "SMTP_SSL", FakeSMTP)
    refused = SmtpSSL("smtp.example.com", 465, "user", "password").send(MESSAGE)

    assert captured["host"] == "smtp.example.com"
    assert captured["port"] == 465
    assert captured["login"] == ("user", "password")
    context = captured["context"]
    assert context.verify_mode == ssl.CERT_REQUIRED
    assert context.check_hostname is True

    emsg = captured["message"]
    assert emsg["From"] == "user"
    assert emsg["To"] == "davidhua@foxmail.com"
    assert emsg["Subject"] == MESSAGE["subject"]
    assert emsg.get_content().strip() == MESSAGE["content"]
    assert refused == {"someone@example.com": (550, b"no such user")}


def test_smtp_ssl_wraps_tls_failures(monkeypatch):
    def fail(*args, **kwargs):
        raise ssl.SSLCertVerificationError("certificate verify failed")

    monkeypatch.setattr(smtp_module.smtplib, "SMTP_SSL", fail)
    with pytest.raises(SmtpError) as excinfo:
        SmtpSSL("smtp.example.com", 465, "user", "password").send(MESSAGE)

    assert isinstance(excinfo.value.__cause__, ssl.SSLCertVerificationError)
