from flask import render_template_string

def test_render_nav_item_active(app, client):
    @app.route('/active')
    def foo():
        return render_template_string('''
                {% from 'macro/nav.html' import render_nav_item %}
                {{ render_nav_item('foo', 'Foo') }}
                ''')

    @app.route('/not_active')
    def bar():
        return render_template_string('''
                {% from 'macro/nav.html' import render_nav_item %}
                {{ render_nav_item('foo', 'Foo') }}
                ''')

    rv = client.get('/active')
    assert '<a class="nav-item nav-link active"' in rv.text

    rv = client.get('/not_active')
    assert '<a class="nav-item nav-link"' in rv.text
