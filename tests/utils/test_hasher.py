from flask_exts.utils.hasher import Blake2bHasher


def test_hasher():
    hh = Blake2bHasher("abc")
    data1 = "test"
    data2 = "test"
    h1 = hh.hash(data1)
    r = hh.verify(data2, h1)
    assert r is True
