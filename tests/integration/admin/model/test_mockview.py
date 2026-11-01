from unittest.mock import MagicMock

from flask import url_for

from flask_exts.admin.model.view import ModelView


def test_mockview_basic(app, admin, blackhole_factory):
    view = ModelView(
        model=MagicMock,
        backend_factory=blackhole_factory,
    )

    endpoint = "magicmock"
    assert view.name == endpoint
    assert view.endpoint == endpoint

    admin.register_view(view)

    with app.test_request_context():
        index_view = url_for(f"{endpoint}.index_view")
        create_view = url_for(f"{endpoint}.create_view")
        edit_view = url_for(f"{endpoint}.edit_view")
        details_view = url_for(f"{endpoint}.details_view")
        delete_view = url_for(f"{endpoint}.delete_view")
        ajax_lookup = url_for(f"{endpoint}.ajax_lookup")
        ajax_update = url_for(f"{endpoint}.ajax_update")
        action_view = url_for(f"{endpoint}.action_view")
        export_view = url_for(f"{endpoint}.export", export_type="exporttype")

        assert index_view == f"/admin/{endpoint}/"
        assert create_view == f"/admin/{endpoint}/new/"
        assert edit_view == f"/admin/{endpoint}/edit/"
        assert details_view == f"/admin/{endpoint}/details/"
        assert delete_view == f"/admin/{endpoint}/delete/"
        assert ajax_lookup == f"/admin/{endpoint}/ajax/lookup/"
        assert ajax_update == f"/admin/{endpoint}/ajax/update/"
        assert action_view == f"/admin/{endpoint}/action/"
        assert export_view == f"/admin/{endpoint}/export/exporttype/"
