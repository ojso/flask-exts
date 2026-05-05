from .forms.form.csrf import get_csrf_token


def init_template_funcs(app):
    app.jinja_env.globals["csrf_token"] = get_csrf_token
