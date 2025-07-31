from flask import render_template_string


def test_render_breadcrumb_item_active(app, client):
    @app.route('/not_active_item')
    def foo():
        return render_template_string('''
                {% from 'macro/nav.html' import render_breadcrumb_item %}
                {{ render_breadcrumb_item('bar', 'Bar') }}
                ''')

    @app.route('/active_item')
    def bar():
        return render_template_string('''
                {% from 'macro/nav.html' import render_breadcrumb_item %}
                {{ render_breadcrumb_item('bar', 'Bar') }}
                ''')

    rv = client.get('/not_active_item')
    assert '<li class="breadcrumb-item">' in rv.text

    rv = client.get('/active_item')
    assert '<li class="breadcrumb-item active" aria-current="page">' in rv.text
