def test_extensions(app):
    # print(app.extensions.keys())
    # print(app.extensions)
    assert "manager" in app.extensions
    assert "babel" in app.extensions
    assert "templating" in app.extensions


def test_blueprints(app):
    print(app.blueprints)
    pass


def test_routes(app):
    rules = list(app.url_map.iter_rules())
    for k in rules:
        print(k.rule, k.endpoint)
    pass


def test_list_templates(app):
    # print("\n===== app.jinja_env.list_templates =====")
    for k in app.jinja_env.list_templates():
        # print(k)
        pass
