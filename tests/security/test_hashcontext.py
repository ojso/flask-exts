from flask_exts.security.hash_context import HashContext
from flask_exts.proxies import _security

def test_hash_context():
    hh = HashContext("abc")
    data1 = "test"
    data2 = "test"
    h1 = hh.hash(data1)
    r = hh.verify(data2, h1)
    assert r is True

def test_security_hash_context(app):
    with app.app_context():
        hh = _security.hash_context
        data1 = "test"
        data2 = "test"
        h1 = hh.hash(data1)
        r = hh.verify(data2, h1)
        assert r is True