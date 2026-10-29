from flask import abort, current_app, jsonify, request
from flask_babel import gettext
from sqlalchemy.exc import SQLAlchemyError
from werkzeug.datastructures import MultiDict

from ...datastore.sqla.utils import get_model_primary_key
from ...forms.form import Form
from ...forms.form.csrf import CSRF_FIELD_NAME
from ..exposer import expose_url
from ..model.view import ModelView
from .backend import SqlaBackend
from .type_formatters import SQLA_FORMATTERS


class SqlaModelView(ModelView):
    """SQLAlchemy model view"""

    column_type_formatters = SQLA_FORMATTERS



    def __init__(self, model, session=None, name=None, endpoint=None, url=None):
        """
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

    @expose_url("/ajax/create-parent/", methods=("POST",))
    def ajax_create_parent(self):
        if not self.inline_models:
            abort(404)
        if not self.can_create:
            abort(403)

        form = self.create_form()
        if not form.validate():
            return jsonify(errors=form.errors), 422

        model = self.create_model(form)
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

        action = payload.get("action")

        related_objects = getattr(parent, relationship_name)
        prefix = payload.get("prefix")
        if (
            not isinstance(prefix, str)
            or not prefix.startswith(f"{relationship_name}-")
            or not prefix.endswith("-")
        ):
            return jsonify(error=gettext("Invalid inline form data.")), 400

        token = payload.get("csrf_token")
        if current_app.config.get("CSRF_ENABLED", True):
            csrf_field_name = current_app.config.get("CSRF_FIELD_NAME", CSRF_FIELD_NAME)
            csrf_form = Form(formdata=MultiDict({csrf_field_name: token or ""}))
            if not csrf_form[csrf_field_name].validate(csrf_form):
                return jsonify(error=gettext("CSRF token is invalid.")), 400

        if action == "delete":
            child_id = payload.get("child_id")
            if child_id is None:
                return jsonify(error=gettext("Related record is required.")), 400

            self.remove_child(parent_id,relationship_name,child_id)

            child = self._get_related_inline_object(
                parent, relationship_name, config, child_id
            )
            if child is None:
                abort(404)
            try:
                if config["is_collection"]:
                    if hasattr(related_objects, "remove"):
                        related_objects.remove(child)
                    elif hasattr(related_objects, "discard"):
                        related_objects.discard(child)
                else:
                    setattr(parent, relationship_name, None)
                self.session.delete(child)
                self.session.commit()
            except SQLAlchemyError:
                self.session.rollback()
                current_app.logger.exception("Failed to delete inline model")
                return (
                    jsonify(error=gettext("Failed to delete related record.")),
                    500,
                )
            return jsonify(message=gettext("Related record deleted."))

        if action != "save":
            return jsonify(error=gettext("Unsupported inline action.")), 400

        values = payload.get("values")
        if not isinstance(values, dict):
            return jsonify(error=gettext("Invalid inline form data.")), 400

        formdata = MultiDict()
        for name, value in values.items():
            if not isinstance(name, str):
                return jsonify(error=gettext("Invalid inline form data.")), 400
            for item in value if isinstance(value, list) else [value]:
                formdata.add(f"{prefix}{name}", "" if item is None else str(item))

        child_form = config["form_class"](
            formdata=formdata,
            prefix=prefix,
        )
        if not child_form.validate():
            return jsonify(errors=child_form.errors), 422

        child_id = payload.get("child_id")
        if child_id is None:
            if not config["is_collection"] and related_objects is not None:
                return jsonify(error=gettext("A related record already exists.")), 409
            child = config["model"]()
        else:
            child = self._get_related_inline_object(
                parent, relationship_name, config, child_id
            )
            if child is None:
                abort(404)

        primary_key = get_model_primary_key(config["model"])
        primary_key_names = (
            primary_key if isinstance(primary_key, tuple) else (primary_key,)
        )
        for name, field in child_form._fields.items():
            if (
                name not in primary_key_names
                and name != config["reverse_prop"]
                and name != child_form.meta.csrf_field_name
            ):
                field.populate_obj(child, name)

        try:
            if child_id is None:
                if config["is_collection"]:
                    if hasattr(related_objects, "add"):
                        related_objects.add(child)
                    else:
                        related_objects.append(child)
                else:
                    setattr(parent, relationship_name, child)
            self.session.add(child)
            self.session.commit()
        except SQLAlchemyError:
            self.session.rollback()
            current_app.logger.exception("Failed to save inline model")
            return jsonify(error=gettext("Failed to save related record.")), 500

        if isinstance(primary_key, tuple):
            saved_child_id = [getattr(child, key) for key in primary_key]
        else:
            saved_child_id = getattr(child, primary_key)
        return jsonify(
            child_id=saved_child_id,
            message=gettext("Related record saved."),
        )
