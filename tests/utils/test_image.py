from flask_exts.utils.image import generate_qr_code


def test_generate_qr_code():
    uri = "http://example.com"
    qr_code_data_url = generate_qr_code(uri)
    assert qr_code_data_url.startswith("data:image/png;base64,")
