from flask import render_template_string, request
from ...models import db, reset_models
from ...models.message import Message

def test_render_pager(app, client):
    @app.route("/pager")
    def test():
        reset_models()
        for i in range(100):
            msg = Message()
            db.session.add(msg)
        db.session.commit()
        page = request.args.get("page", 1, type=int)
        pagination = Message.query.paginate(page=page, per_page=10)
        messages = pagination.items
        return render_template_string(
            """
            {% from 'bootstrap4/pagination.html' import render_pager %}
            {{ render_pager(pagination) }}
            """,
            pagination=pagination,
            messages=messages,
        )

    rv = client.get("/pager")
    assert '<nav aria-label="Page navigation">' in rv.text
    assert "Previous" in rv.text
    assert "Next" in rv.text
    assert '<li class="page-item disabled">' in rv.text

    rv = client.get("/pager?page=2")
    assert '<nav aria-label="Page navigation">' in rv.text
    assert "Previous" in rv.text
    assert "Next" in rv.text
    assert '<li class="page-item disabled">' not in rv.text
