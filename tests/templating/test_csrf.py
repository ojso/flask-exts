from flask import render_template_string
from flask_exts.templating.csrf import generate_csrf, validate_csrf


def test_csrf(app):
    with app.test_request_context():
        validate_csrf(generate_csrf())


def test_render_token(app):
    with app.test_request_context():
        token = generate_csrf()
        assert render_template_string("{{ csrf_token() }}") == token
