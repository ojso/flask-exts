def get_app_endpoint_rule(app, endpoint):
    rules = list(app.url_map.iter_rules())
    for k in rules:
        if k.endpoint == endpoint:
            return k.rule


def print_app_endpoint_rule(app):
    rules = list(app.url_map.iter_rules())
    for k in rules:
        print(k.endpoint, k.rule)


def print_blueprints(app):
    print("\n===== app.blueprints =====")
    # print(app.blueprints)
    for k, v in app.blueprints.items():
        print(k, v, v.static_folder)


def print_routes(app):
    print("\n===== app.url_map =====")
    rules = list(app.url_map.iter_rules())
    for k in rules:
        print(k.endpoint, k.rule, app.view_functions[k.endpoint])
    # for k in rules:
    #     print(k.rule, k.endpoint)
    # for k,v in app.view_functions.items():
    #     print(k, v)


def print_list_templates(app):
    print("\n===== app.jinja_env.list_templates =====")
    for k in app.jinja_env.list_templates():
        print(k)
