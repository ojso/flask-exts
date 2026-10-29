def print_list_templates(app):
    print("\n===== app.jinja_env.list_templates =====")
    for k in app.jinja_env.list_templates():
        print(k)


def test_jinja_globals(app):
    assert "_template" in app.jinja_env.globals
    assert "csrf_token" in app.jinja_env.globals
