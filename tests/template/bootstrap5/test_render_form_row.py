from flask import render_template_string


def test_render_form_row(app, client, hello_form):
    @app.route("/form")
    def test():
        form = hello_form()
        return render_template_string(
            """
            {% from 'bootstrap5/form.html' import render_form_row %}
            {{ render_form_row([form.username, form.password]) }}
            """,
            form=form,
        )

    rv = client.get("/form")
    assert '<div class="form-row">' not in rv.text
    assert '<div class="row">' in rv.text
    assert '<div class="col">' in rv.text
