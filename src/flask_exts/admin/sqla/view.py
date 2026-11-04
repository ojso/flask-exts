from flask import abort, current_app, jsonify, request
from flask_babel import gettext
from werkzeug.datastructures import MultiDict

from ...forms.form import Form
from ...forms.form.csrf import CSRF_FIELD_NAME
from ..exposer import expose_url
from ..model.view import ModelView
from .backend import InlineModelError, SqlaBackend
from .type_formatters import SQLA_FORMATTERS


class SqlaModelView(ModelView):
    """SQLAlchemy model view"""

    column_type_formatters = SQLA_FORMATTERS

    inline_models = None
    """Child models to include as inline forms."""

    def __init__(self, model, session=None, name=None, endpoint=None, url=None):
        """Initialize the SQLAlchemy model view.

        Args:
            model: Model class
            session: SQLAlchemy session
            name: View name.
            endpoint: Endpoint name.
            url: Base URL.
        """
        super().__init__(model, SqlaBackend, name, endpoint, url, session=session)

    def _init_handlers(self):
        return super()._init_handlers()

    def _init_components(self, **kwargs):
        super()._init_components()
        # backend
        self._backend.init_auto_joins()
        if self.form_choices is None:
            self.form_choices = {}

    def remove_inline_child(self, parent, relationship_name, child_id):
        return self._backend.remove_inline_child(parent, relationship_name, child_id)

    def save_inline_child(self, parent, relationship_name, child_id, values):
        return self._backend.save_inline_child(
            parent, relationship_name, child_id, values
        )

    @expose_url("/ajax/create-parent/", methods=("POST",))
    def ajax_create_parent(self):
        if not self.inline_models:
            abort(404)
        if not self.can_create:
            abort(403)

        form = self.create_form()
        if not form.validate():
            return jsonify(errors=form.errors), 422

        model_instance = self.model()
        form.populate_obj(model_instance)
        model = self.create_model(model_instance)
        if model is None:
            return jsonify(error=gettext("Failed to create the parent record.")), 500

        return jsonify(
            id=self.get_pk_value(model),
            redirect_url=self.get_url(".edit_view", id=self.get_pk_value(model)),
        )

    @expose_url(
        "/ajax/inline/<relationship_name>/",
        methods=("POST",),
    )
    def ajax_inline_model(self, relationship_name):
        if not request.is_json:
            abort(400)
        if not self.can_edit:
            abort(403)

        payload = request.get_json()
        if not isinstance(payload, dict):
            return jsonify(error=gettext("Invalid request data.")), 400

        parent_id = payload.get("parent_id")
        if parent_id is None:
            return jsonify(error=gettext("Parent record is required.")), 400
        parent = self.get_one(str(parent_id))
        if parent is None:
            abort(404)

        token = payload.get("csrf_token")
        if current_app.config.get("CSRF_ENABLED", True):
            csrf_field_name = current_app.config.get("CSRF_FIELD_NAME", CSRF_FIELD_NAME)
            csrf_form = Form(formdata=MultiDict({csrf_field_name: token or ""}))
            if not csrf_form[csrf_field_name].validate(csrf_form):
                return jsonify(error=gettext("CSRF token is invalid.")), 400

        action = payload.get("action")
        child_id = payload.get("child_id")

        if action == "delete":
            if child_id is None:
                return jsonify(error=gettext("Related record is required.")), 400

            try:
                self.remove_inline_child(parent, relationship_name, child_id)
            except LookupError:
                abort(404)
            return jsonify(message=gettext("Related record deleted."))
        elif action == "save":
            values = payload.get("values")
            if not isinstance(values, dict):
                return jsonify(error=gettext("Invalid inline form data.")), 400

            try:
                saved_child_id = self.save_inline_child(
                    parent, relationship_name, child_id, values
                )
            except LookupError:
                abort(404)
            except InlineModelError as exc:
                response = {"error": exc.message}
                if exc.errors:
                    response["errors"] = exc.errors
                return jsonify(response), exc.status_code

            return jsonify(
                child_id=saved_child_id,
                message=gettext("Related record saved."),
            )
        else:
            return jsonify(error=gettext("Unsupported inline action.")), 400
