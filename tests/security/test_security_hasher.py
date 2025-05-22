from flask_exts.proxies import _security


def test_security_hasher(app):
    with app.app_context():
        security_hasher = _security.hasher
        data1 = "test"
        data2 = "test"
        h1 = security_hasher.hash(data1)
        r = security_hasher.verify(data2, h1)
        assert r is True
