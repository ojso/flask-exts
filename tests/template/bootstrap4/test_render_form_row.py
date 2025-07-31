from flask import render_template_string


def test_render_form_row(app, client, hello_form):
    @app.route("/form")
    def test():
        form = hello_form()
        return render_template_string(
            """
            {% from 'bootstrap4/form.html' import render_form_row %}
            {{ render_form_row([form.username, form.password]) }}
            """,
            form=form,
        )

    rv = client.get("/form")
    assert '<div class="form-row">' in rv.text
    assert '<div class="col">' in rv.text


def test_render_form_row_row_class(app, client, hello_form):
    @app.route("/form")
    def test():
        form = hello_form()
        return render_template_string(
            """
            {% from 'bootstrap4/form.html' import render_form_row %}
            {{ render_form_row([form.username, form.password], row_class='row') }}
            """,
            form=form,
        )

    rv = client.get("/form")
    assert '<div class="row">' in rv.text


def test_render_form_row_col_class_default(app, client, hello_form):
    @app.route("/form")
    def test():
        form = hello_form()
        return render_template_string(
            """
            {% from 'bootstrap4/form.html' import render_form_row %}
            {{ render_form_row([form.username, form.password], col_class_default='col-md-6') }}
            """,
            form=form,
        )

    rv = client.get("/form")
    assert '<div class="col-md-6">' in rv.text


def test_render_form_row_col_map(app, client, hello_form):
    @app.route("/form")
    def test():
        form = hello_form()
        return render_template_string(
            """
            {% from 'bootstrap4/form.html' import render_form_row %}
            {{ render_form_row([form.username, form.password], col_map={'username': 'col-md-6'}) }}
            """,
            form=form,
        )

    rv = client.get("/form")
    assert '<div class="col">' in rv.text
    assert '<div class="col-md-6">' in rv.text
