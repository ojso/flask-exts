from flask import render_template_string


def test_render_field(app, client, hello_form):
    @app.route("/field")
    def test():
        form = hello_form()
        return render_template_string(
            """
            {% from 'bootstrap4/form.html' import render_field %}
            {{ render_field(form.csrf_token) }}
            {{ render_field(form.hidden) }}
            {{ render_field(form.username) }}
            {{ render_field(form.password) }}
            """,
            form=form,
        )

    rv = client.get("/field")
    assert (
        '<label class="form-control-label" for="csrf_token">CSRF Token</label>'
        not in rv.text
    )
    assert '<label class="form-control-label" for="hidden">Hidden</label>' not in rv.text
    assert '<input class="form-control" id="username"' in rv.text
    assert '<input class="form-control" id="password"' in rv.text


def test_render_field_with_render_kw_classes(app, client, hello_form):
    @app.route("/render_kw_class")
    def test_render_kw_class():
        form = hello_form()
        form.name.render_kw = {"class": "render_kw_class"}
        form.username.render_kw = {"class": "render_kw_class"}
        form.password.render_kw = {"class": "render_kw_class"}
        return render_template_string(
            """
            {% from 'bootstrap4/form.html' import render_field %}
            {{ render_field(form.name) }}
            {{ render_field(form.username, class_='test') }}
            {{ render_field(form.password, class='test') }}
            """,
            form=form,
        )

    rv = client.get("/render_kw_class")
    assert '<input class="form-control render_kw_class" id="name" name="name"' in rv.text
    assert '<input class="form-control test" id="username"' in rv.text
    assert '<input class="form-control test" id="password"' in rv.text


def test_render_field_with_kwargs(app, client, hello_form):
    @app.route("/kwargs_class")
    def test_kwargs_class():
        form = hello_form()
        return render_template_string(
            """
            {% from 'bootstrap4/form.html' import render_field %}
            {{ render_field(form.username, class_='test') }}
            {{ render_field(form.password, class='test') }}
            """,
            form=form,
        )

    @app.route("/general_kwargs")
    def test_general_kwargs():
        form = hello_form()
        return render_template_string(
            """
            {% from 'bootstrap4/form.html' import render_field %}
            {{ render_field(form.username, placeholder='test') }}
            {{ render_field(form.password, placeholder='test') }}
            {{ render_field(form.remember, class='test', value='n') }}
            {{ render_field(form.submit, value='test') }}
            """,
            form=form,
        )

    rv = client.get("/kwargs_class")
    assert '<input class="form-control test" id="username"' in rv.text
    assert '<input class="form-control test" id="password"' in rv.text

    rv = client.get("/general_kwargs")
    # print(data)
    assert 'name="username" placeholder="test"' in rv.text
    assert 'name="password" placeholder="test"' in rv.text
    assert (
        '<input class="form-check-input test" id="remember" name="remember" type="checkbox" value="n"'
        in rv.text
    )
    assert (
        '<input class="btn btn-primary btn-md" id="submit" name="submit" type="submit" value="test"'
        in rv.text
    )
