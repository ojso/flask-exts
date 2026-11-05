import pytest

from flask_exts.emailer.smtp import SmtpSSL


def test_email(app):
    real_email_sender = app.config.get("REAL_EMAIL_SENDER")
    if not real_email_sender:
        pytest.skip("REAL_EMAIL_SENDER is not configured")

    # set to's email
    to = "david.dong.hua@gmail.com"
    content = "This is a test email."
    subject = "This is a test subject."
    data = {
        "to": to,
        "subject": subject,
        "content": content,
    }

    s = SmtpSSL(**real_email_sender)
    r = s.send(data)
    # print(f"send result: {r}")
    assert not r
