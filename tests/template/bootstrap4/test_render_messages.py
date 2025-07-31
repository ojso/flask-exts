from flask import flash, render_template_string


def test_render_messages(app, client):
    @app.route("/messages")
    def test_messages():
        flash("test message", "danger")
        return render_template_string(
            """
            {% from 'bootstrap4/message.html' import render_messages %}
            {{ render_messages() }}
            """
        )

    @app.route("/container")
    def test_container():
        flash("test message", "danger")
        return render_template_string(
            """
            {% from 'bootstrap4/message.html' import render_messages %}
            {{ render_messages(container=True) }}
            """
        )

    @app.route("/dismissible")
    def test_dismissible():
        flash("test message", "danger")
        return render_template_string(
            """
            {% from 'bootstrap4/message.html' import render_messages %}
            {{ render_messages(dismissible=True) }}
            """
        )

    @app.route("/dismiss_animate")
    def test_dismiss_animate():
        flash("test message", "danger")
        return render_template_string(
            """
            {% from 'bootstrap4/message.html' import render_messages %}
            {{ render_messages(dismissible=True, dismiss_animate=True) }}
            """
        )

    rv = client.get("/messages")
    assert '<div class="alert alert-danger"' in rv.text

    rv = client.get("/container")
    assert '<div class="container flashed-messages">' in rv.text

    rv = client.get("/dismissible")
    assert "alert-dismissible" in rv.text
    assert '<button type="button" class="close" data-dismiss="alert"' in rv.text
    assert "fade show" not in rv.text

    rv = client.get("/dismiss_animate")
    assert "alert-dismissible" in rv.text
    assert '<button type="button" class="close" data-dismiss="alert"' in rv.text
    assert "fade show" in rv.text
