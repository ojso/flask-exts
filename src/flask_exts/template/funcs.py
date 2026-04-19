from wtforms import HiddenField
from .forms.form.csrf import get_csrf_token


class Funcs:
    """Template functions for Flask applications."""

    def type_name(self, item):
        return type(item).__name__

    def get_table_titles(self, data, primary_key, primary_key_title):
        """Detect and build the table titles tuple from ORM object, currently only support SQLAlchemy."""
        if not data:
            return []
        titles = []
        for k in data[0].__table__.columns.keys():
            if not k.startswith("_"):
                titles.append((k, k.replace("_", " ").title()))
        titles[0] = (primary_key, primary_key_title)
        return titles

    def csrf_token(self):
        return get_csrf_token()
