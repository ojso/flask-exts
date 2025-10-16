from flask import render_template_string


def test_render_icon(app, client):
    @app.route("/icon")
    def icon():
        return render_template_string(
            """
            {% from 'macro/icon.html' import render_icon %}
                {{ render_icon('heart') }}
            """
        )

    @app.route("/icon-size")
    def icon_size():
        return render_template_string(
            """
            {% from 'macro/icon.html' import render_icon %}
                {{ render_icon('heart', 32) }}
            """
        )

    @app.route("/icon-style")
    def icon_style():
        return render_template_string(
            """
            {% from 'macro/icon.html' import render_icon %}
                {{ render_icon('heart', color='primary') }}
            """
        )

    @app.route("/icon-color")
    def icon_color():
        return render_template_string(
            """
            {% from 'macro/icon.html' import render_icon %}
                {{ render_icon('heart', color='green') }}
            """
        )

    @app.route("/icon-title")
    def icon_title():
        return render_template_string(
            """
            {% from 'macro/icon.html' import render_icon %}
                {{ render_icon('heart', title='Heart') }}
            """
        )

    @app.route("/icon-desc")
    def icon_desc():
        return render_template_string(
            """
            {% from 'macro/icon.html' import render_icon %}
                {{ render_icon('heart', desc='A heart.') }}
            """
        )

    rv = client.get("/icon")
    assert "bootstrap-icons.svg#heart" in rv.text
    assert 'width="1em"' in rv.text
    assert 'height="1em"' in rv.text
    assert 'class="bi"' in rv.text
    assert 'fill="currentColor"' in rv.text

    rv = client.get("/icon-size")
    assert "bootstrap-icons.svg#heart" in rv.text
    assert 'width="32"' in rv.text
    assert 'height="32"' in rv.text

    rv = client.get("/icon-style")
    assert "bootstrap-icons.svg#heart" in rv.text
    assert 'class="bi text-primary"' in rv.text
    assert 'fill="currentColor"' in rv.text

    rv = client.get("/icon-color")
    assert "bootstrap-icons.svg#heart" in rv.text
    assert "bootstrap-icons.svg#heart" in rv.text
    assert 'class="bi"' in rv.text
    assert 'fill="green"' in rv.text

    rv = client.get("/icon-title")
    assert "bootstrap-icons.svg#heart" in rv.text
    assert "<title>Heart</title>" in rv.text

    rv = client.get("/icon-desc")
    assert "bootstrap-icons.svg#heart" in rv.text
    assert "<desc>A heart.</desc>" in rv.text
