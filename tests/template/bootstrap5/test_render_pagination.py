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

    response = client.get("/pagination")
    data = response.get_data(as_text=True)
    assert '<nav aria-label="Page navigation">' in data
    assert (
        '<a class="page-link" href="#">1 <span class="sr-only">(current)</span></a>'
        not in data
    )
    assert '<li class="page-item active" aria-current="page">' in data
    assert '<a class="page-link" href="#">1</a>' in data
