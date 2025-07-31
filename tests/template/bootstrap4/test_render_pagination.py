from flask import render_template_string, request
from ...models import db, reset_models
from ...models.message import Message


def test_render_pagination(app, client):
    @app.route("/pagination")
    def test():
        reset_models()
        for i in range(100):  # noqa: F841
            msg = Message()
            db.session.add(msg)
        db.session.commit()
        page = request.args.get("page", 1, type=int)
        pagination = Message.query.paginate(page=page, per_page=10)
        messages = pagination.items
        return render_template_string(
            """
            {% from 'bootstrap4/pagination.html' import render_pagination %}
            {{ render_pagination(pagination) }}
            """,
            pagination=pagination,
            messages=messages,
        )

    rv = client.get("/pagination")
    assert '<nav aria-label="Page navigation">' in rv.text
    assert '<a class="page-link" href="#">1</a>' in rv.text
    assert "10</a>" in rv.text

    rv = client.get("/pagination?page=2")
    assert '<nav aria-label="Page navigation">' in rv.text
    assert "1</a>" in rv.text
    assert '<a class="page-link" href="#">2</a>' in rv.text
    assert "10</a>" in rv.text
