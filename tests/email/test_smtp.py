import pytest
from flask_exts.email.smtp import SmtpSSL


@pytest.mark.skip(reason="password is empty")
def test_email():
    host = "smtp.qiye.aliyun.com"
    port = "465"
    user = "test@ojso.com"
    password = ""  # uncomment this line to test with empty password
    # password = "gTk94GEeNvujr4zm"

    # set to's email
    to = "test@ojso.com"
    content = "This is a test email."
    subject = "This is a test subject."
    data = {
        "to": to,
        "subject": subject,
        "content": content,
    }

    s = SmtpSSL(host, port, user, password)
    r = s.send(data)
    # print(f"send result: {r}")
    assert not r
