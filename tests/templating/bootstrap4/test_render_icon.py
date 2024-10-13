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

    response = client.get("/icon")
    data = response.get_data(as_text=True)
    assert "bootstrap-icons.svg#heart" in data
    assert 'width="1em"' in data
    assert 'height="1em"' in data
    assert 'class="bi"' in data
    assert 'fill="currentColor"' in data

    response = client.get("/icon-size")
    data = response.get_data(as_text=True)
    assert "bootstrap-icons.svg#heart" in data
    assert 'width="32"' in data
    assert 'height="32"' in data

    response = client.get("/icon-style")
    data = response.get_data(as_text=True)
    assert "bootstrap-icons.svg#heart" in data
    assert 'class="bi text-primary"' in data
    assert 'fill="currentColor"' in data

    response = client.get("/icon-color")
    data = response.get_data(as_text=True)
    assert "bootstrap-icons.svg#heart" in data
    assert 'class="bi"' in data
    assert 'fill="green"' in data

    response = client.get("/icon-title")
    data = response.get_data(as_text=True)
    assert "bootstrap-icons.svg#heart" in data
    assert "<title>Heart</title>" in data

    response = client.get("/icon-desc")
    data = response.get_data(as_text=True)
    assert "bootstrap-icons.svg#heart" in data
    assert "<desc>A heart.</desc>" in data
