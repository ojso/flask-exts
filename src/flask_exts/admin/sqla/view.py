
from flask import abort, current_app, flash, jsonify, request
from flask_babel import gettext
from sqlalchemy import inspect
from sqlalchemy.exc import SQLAlchemyError
from werkzeug.datastructures import MultiDict

from ...datastore.sqla import db
from ...datastore.sqla.query import Query
from ...datastore.sqla.utils import (
    get_instance_identity,
    get_model_column_type,
    get_model_primary_key,
)
from ...forms.form import Form
from ...forms.form.csrf import CSRF_FIELD_NAME
from ..exposer import expose_url
from ..model.view import ModelView
from .ajax import create_ajax_loader
from .filter import FilterConverter
from .form import get_model_form
from .form.inline_model_convert import InlineModelConverter
from .form.model_field_convert import ModelFieldConverter
from .type_formatters import DEFAULT_FORMATTERS


class SqlaModelView(ModelView):
    """
    SQLAlchemy model view
    """

    model_field_converter = ModelFieldConverter
    """
        Model field conversion class. Use this to implement custom field conversion logic.

        For example::

            class MyModelFieldConverter(ModelFieldConverter):
                pass

            class MyAdminView(ModelView):
                model_field_converter = MyModelFieldConverter
    """

    inline_model_converter = InlineModelConverter
    """
        Inline model conversion class. If you need some kind of post-processing for inline
        forms, you can customize behavior by doing something like this::

            class MyInlineModelConverter(InlineModelConverter):
                def post_process(self, form_class, info):
                    form_class.value = wtf.StringField('value')
                    return form_class

            class MyAdminView(ModelView):
                inline_model_converter = MyInlineModelConverter
    """

    inline_models = None
    """
        Inline related-model editing for models with parent-child relations.
        Related rows are managed independently through AJAX; a new parent
        record is created before its inline rows can be added.

        Accepts enumerable with one of the following possible values:

        1. Child model class::

            class MyModelView(ModelView):
                inline_models = (Post,)

        2. Child model class and additional options::

            class MyModelView(ModelView):
                inline_models = [(Post, {"form_columns": ["title"]})]

        3. Django-like ``InlineForm`` class instance::

            from .model.form import InlineForm

            class MyInlineForm(InlineForm):
                form_columns = ('title', 'date')

            class MyModelView(ModelView):
                inline_models = (MyInlineForm(MyInlineModel),)

        You can customize the generated field name by:

        1. Using the `form_name` property as a key to the options dictionary::

            class MyModelView(ModelView):
                inline_models = ((Post, {"form_label": "Hello"}))

        2. Using forward relation name and `column_labels` property::

            class Model1(Base):
                pass

            class Model2(Base):
                # ...
                model1 = relation(Model1, backref='models')

            class MyModel1View(Base):
                inline_models = (Model2,)
                column_labels = {'models': 'Hello'}

        By default used ManyToMany relationship for inline models.
        You may configure inline model for OneToOne relationship.
        To achieve this, you need to install special ``inline_model_converter``
        for your model::

            from .sqla.form import InlineOneToOneModelConverter

            class MyInlineForm(InlineForm):
                form_columns = ('title', 'date')
                inline_model_converter = InlineOneToOneModelConverter

            class MyModelView(ModelView):
                inline_models = (MyInlineForm(MyInlineModel),)
    """

    column_type_formatters = DEFAULT_FORMATTERS

    form_choices: dict[str, list[tuple[str, str]]] | None = None
    """
        Map choices to form fields

        Example::

            class MyModelView(BaseModelView):
                form_choices = {'my_form_field': [
                    ('db_value', 'display_value'),
                ]}
    """

    def __init__(
        self,
        model,
        session=None,
        name=None,
        endpoint=None,
        url=None,
        static_folder=None,
    ):
        """
        Constructor.

        Args:
            model:
                Model class
            session:
                SQLAlchemy session
            name:
                View name. If not set, defaults to the model name
            endpoint:
                Endpoint name. If not set, defaults to the model name
            url:
                Base URL. If not set, defaults to '/admin/' + endpoint
        """

        self.session = session or db.session
        self.filter_converter = FilterConverter()

        super().__init__(
            model,
            name,
            endpoint,
            url,
            static_folder,
        )

        if self.form_choices is None:
            self.form_choices = {}

        self._primary_key = get_model_primary_key(self.model)
        self._is_multiple_pk = isinstance(self._primary_key, tuple)

        if self._primary_key is None:
            raise Exception("Model %s does not have primary key." % self.model.__name__)

        self._auto_joins = self._init_auto_joins()

    def _init_auto_joins(self):
        """
        Return a list of joined tables by going through the displayed columns.
        """
        manytoone_relations = set()
        manytomany_relations = set()
        list_columns = set()

        mapper = inspect(self.model)
        for p in mapper.attrs:
            if hasattr(p, "direction"):
                if p.direction.name in ["MANYTOONE"]:
                    manytoone_relations.add(p.key)
                elif p.direction.name in ["MANYTOMANY", "ONETOMANY"]:
                    manytomany_relations.add(p.key)

        joinedloads = []
        selectinloads = []

        for prop, _name in self._list_columns:
            list_columns.add(prop.split(".", 1)[0])

        for prop in manytoone_relations.intersection(list_columns):
            joinedloads.append(getattr(self.model, prop))

        for prop in manytomany_relations.intersection(list_columns):
            selectinloads.append(getattr(self.model, prop))

        return (joinedloads, selectinloads)

    def get_pk_value(self, instance):
        """
        Return the primary key value from a model object.
        If there are multiple primary keys, they're encoded into string representation.
        """
        value = get_instance_identity(instance)
        if isinstance(value, tuple):
            return ",".join([str(v) for v in value])
        else:
            return str(value)

    def scaffold_list_columns(self):
        """
        Return a list of columns from the model.
        """
        columns = []

        mapper = inspect(self.model)
        for p in mapper.attrs:
            if hasattr(p, "direction"):
                if p.direction.name in ["MANYTOONE", "MANYTOMANY"]:
                    columns.append(p.key)
            elif hasattr(p, "columns"):
                column = p.columns[0]
                if column.foreign_keys:
                    continue
                columns.append(p.key)

        return columns

    def scaffold_sortable_columns(self):
        """
        Return a dictionary of sortable columns.
        Key is column name, value is sort column/field.
        """
        columns = {}
        mapper = inspect(self.model)
        for p in mapper.column_attrs:
            if hasattr(p, "columns"):
                if len(p.columns) > 1:
                    # Multi-column properties are not supported
                    continue
                column = p.columns[0]
                # skip foreign keys
                if column.foreign_keys:
                    continue
                columns[p.key] = p.key

        return columns

    def scaffold_filter(self, column_path):
        """
        Return list of enabled filters
        """

        column_type = get_model_column_type(self.model, column_path)

        if self.column_labels and column_path in self.column_labels:
            visible_name = self.column_labels[column_path]
        else:
            visible_name = column_path

        flts = self.filter_converter.get_filters(
            column_type,
            column_path,
            visible_name,
            options=self.column_choices.get(column_path),
        )
        return flts

    def scaffold_form(self):
        """
        Create form from the model.
        """
        converter = self.model_field_converter(self.session, self)

        form_class = get_model_form(
            self.model,
            converter,
            base_class=self.base_form_class,
            only=self.form_columns,
            exclude=self.form_excluded_columns,
            field_args=self.form_args,
            extra_fields=self.form_extra_fields,
        )

        if self.inline_models:
            form_class = self.scaffold_inline_models_form(form_class)

        return form_class

    def scaffold_list_form(self, widget=None, validators=None):
        """
        Create form for the `index_view` using only the columns from
        `self.column_editable_list`.

        Args:
            widget:
                WTForms widget class. Defaults to `EditableWidget`.
            validators:
                `form_args` dict with only validators
                {'name': {'validators': [required()]}}
        """
        converter = self.model_field_converter(self.session, self)
        form_class = get_model_form(
            self.model,
            converter,
            base_class=self.base_form_class,
            only=self.column_editable_list,
            field_args=validators,
        )

        return self.create_editable_list_form(form_class, widget)

    def scaffold_inline_models_form(self, form_class):
        """
        Contribute inline models to the form

        Args:
            form_class:
                Form class
        """
        default_converter = self.inline_model_converter(
            self.session, self, self.model_field_converter
        )

        for m in self.inline_models:
            if hasattr(m, "inline_model_converter"):
                custom_converter = m.inline_model_converter(
                    self.session, self, self.model_field_converter
                )
                form_class = custom_converter.contribute(self.model, form_class, m)
            else:
                form_class = default_converter.contribute(self.model, form_class, m)
        return form_class

    @staticmethod
    def _normalize_inline_pk(value):
        if isinstance(value, (tuple, list)):
            return tuple(str(part) for part in value)
        return str(value)

    def _get_inline_model_config(self, relationship_name):
        if not getattr(self, "_inline_model_configs", None):
            self.scaffold_form()
        config = getattr(self, "_inline_model_configs", {}).get(relationship_name)
        if config is None:
            abort(404)
        return config

    def _get_related_inline_object(self, parent, relationship_name, config, child_id):
        relationship = getattr(parent, relationship_name)
        related = (
            relationship
            if config["is_collection"]
            else ([relationship] if relationship else [])
        )
        normalized_id = self._normalize_inline_pk(child_id)
        for obj in related:
            primary_key = get_model_primary_key(config["model"])
            if isinstance(primary_key, tuple):
                object_id = tuple(str(getattr(obj, key)) for key in primary_key)
            else:
                object_id = str(getattr(obj, primary_key))
            if object_id == normalized_id:
                return obj
        return None

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
            redirect_url=self.get_url(
                ".edit_view", id=self.get_pk_value(model)
            ),
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

        config = self._get_inline_model_config(relationship_name)
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
            csrf_field_name = current_app.config.get(
                "CSRF_FIELD_NAME", CSRF_FIELD_NAME
            )
            csrf_form = Form(formdata=MultiDict({csrf_field_name: token or ""}))
            if not csrf_form[csrf_field_name].validate(csrf_form):
                return jsonify(error=gettext("CSRF token is invalid.")), 400

        if action == "delete":
            child_id = payload.get("child_id")
            if child_id is None:
                return jsonify(error=gettext("Related record is required.")), 400
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

    def _create_ajax_loader(self, name, options):
        return create_ajax_loader(self.model, self.session, name, name, options)

    def _apply_search(self, query: Query, search):
        query.add_search_term(search, self.column_searchable_list)

    def _apply_filters(self, query: Query, filters):
        for idx, flt_name, value in filters:
            flt = self._filters[idx]
            clean_value = flt.clean(value)
            flt.apply(query, clean_value)

    def _apply_sorting(self, query: Query, sort_column, sort_desc):
        if sort_column is not None:
            if sort_column in self._sortable_columns:
                sort_field = self._sortable_columns[sort_column]
                if isinstance(sort_field, (list, tuple)):
                    for field_item in sort_field:
                        query.add_order_by(field_item, sort_desc)
                else:
                    query.add_order_by(sort_field, sort_desc)
        else:
            if default_order := self._get_default_order():
                for default_sort_field, default_sort_desc in default_order:
                    query.add_order_by(default_sort_field, default_sort_desc)

    def _apply_pagination(self, query: Query, page, page_size):
        if page_size is None:
            page_size = self.page_size
        if page_size:
            query.limit(page_size)
        if page and page_size:
            query.offset(page * page_size)

    def _apply_auto_joins(self, query: Query):
        joinedloads, selectinloads = self._auto_joins
        query.add_eager_loads(joinedloads, selectinloads)

    def get_list(
        self,
        page,
        sort_column,
        sort_desc,
        search,
        filters,
        page_size=None,
    ):
        """
        Return records from the database.

        Args:
            page:
                Page number
            sort_column:
                Sort column name
            sort_desc:
                Descending or ascending sort
            search:
                Search query
            execute:
                Execute query immediately? Default is `True`
            filters:
                List of filter tuples
            page_size:
                Number of results. Defaults to ModelView's page_size. Can be
                overriden to change the page_size limit. Removing the page_size
                limit requires setting page_size to 0 or False.
        """

        query = Query(self.model)

        # Apply search criteria
        if search:
            self._apply_search(query, search)

        # Apply filters
        if filters:
            self._apply_filters(query, filters)

        # Auto join
        self._apply_auto_joins(query)

        # get count
        stmt_count = query.build_count()
        count = self.session.scalar(stmt_count)

        # Pagination
        self._apply_pagination(query, page, page_size)

        self._apply_sorting(query, sort_column, sort_desc)

        stmt = query.build()
        result = self.session.execute(stmt).scalars().all()

        return count, result

    def get_one(self, id):
        """
        Return a single model by its id.

        Args:
            id:
                Model id
        """
        if self._is_multiple_pk:
            id = tuple(id.split(","))
        return self.session.get(self.model, id)

    def create_model(self, form):
        """
        Create model from form.

        Args:
            form:
                Form instance
        """
        try:
            instance = self.model()
            form.populate_obj(instance)
            self.session.add(instance)
            self.session.commit()
        except Exception as ex:
            self.session.rollback()
            flash(
                gettext("Failed to create record. %(error)s", error=str(ex)),
                "error",
            )
            return None
        return instance

    def update_model(self, form, model):
        """
        Update model from form.

        Args:
            form:
                Form instance
            model:
                Model instance
        """
        try:
            form.populate_obj(model)
            self.session.commit()
        except Exception as ex:
            self.session.rollback()
            flash(
                gettext("Failed to update record. %(error)s", error=str(ex)),
                "error",
            )
            return False
        return True

    def delete_model(self, model):
        try:
            self.session.delete(model)
            self.session.commit()
            return True
        except Exception as ex:
            flash(
                gettext("Failed to delete record. %(error)s", error=str(ex)),
                "error",
            )
            self.session.rollback()
            return False

    def delete_models_by_pk_ids(self, ids: list):
        try:
            stmt = Query.delete_by_pk_ids(self.model, ids)
            result = self.session.execute(stmt)
            self.session.commit()
            return result.rowcount
        except SQLAlchemyError:
            self.session.rollback()
            raise
