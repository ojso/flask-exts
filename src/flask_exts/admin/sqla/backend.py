from sqlalchemy import inspect
from sqlalchemy.exc import SQLAlchemyError

from ...datastore.sqla import db
from ...datastore.sqla.query import Query
from ...datastore.sqla.utils import (
    get_instance_identity,
    get_model_column_type,
    get_model_primary_key,
)
from ..model import DataBackend
from .ajax import AjaxSqlaModelLoader
from .filter.filter_converter import FilterConverter
from .form import get_model_form
from .form.inline_model_convert import InlineModelConverter
from .form.model_field_convert import ModelFieldConverter


class SqlaBackend(DataBackend):
    def __init__(self, model, view, **kwargs):
        super().__init__(model, view)
        self.session = kwargs.get("session") if kwargs.get("session") else db.session
        self._primary_key = get_model_primary_key(self.model)
        self._is_multiple_pk = isinstance(self._primary_key, tuple)

        if self._primary_key is None:
            raise ValueError(f"Model {self.model.__name__} does not have primary key.")
        self.filter_converter = FilterConverter()
        self.model_field_converter = ModelFieldConverter

        self.inline_model_converter = InlineModelConverter
        """Inline model conversion class.

        If you need some kind of post-processing for inline forms, you can
        customize behavior by doing something like this::

            class MyInlineModelConverter(InlineModelConverter):
                def post_process(self, form_class, info):
                    form_class.value = wtf.StringField('value') return
                    form_class

            inline_model_converter = MyInlineModelConverter
        """

    def init_auto_joins(self):
        """Return a list of joined tables by going through the displayed columns."""
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

        for prop, _name in self.view.get_list_columns():
            list_columns.add(prop.split(".", 1)[0])

        for prop in manytoone_relations.intersection(list_columns):
            joinedloads.append(getattr(self.model, prop))

        for prop in manytomany_relations.intersection(list_columns):
            selectinloads.append(getattr(self.model, prop))

        self._auto_joins = (joinedloads, selectinloads)

    # --- Column / sortable-column / filter / form metadata -------------

    def scaffold_list_columns(self):
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
        """Return list of enabled filters."""
        column_type = get_model_column_type(self.model, column_path)
        visible_name = self.view.get_column_label(column_path, column_path)

        flts = self.filter_converter.get_filters(
            column_type,
            column_path,
            visible_name,
            options=(self.view.column_choices or {}).get(column_path),
        )
        return flts

    def scaffold_form(self, form_type=None):
        converter = self.model_field_converter(self.session, self.view)

        if form_type == "create":
            form_columns = self.view.create_form_columns or self.view.form_columns
        else:
            form_columns = self.view.form_columns

        form_class = get_model_form(
            self.model,
            converter,
            base_class=self.view.base_form_class,
            only=form_columns,
            exclude=self.view.form_excluded_columns,
            field_args=self.view.form_args,
            extra_fields=self.view.form_extra_fields,
        )

        if form_type == "edit" and self.view.inline_models:
            form_class = self.scaffold_inline_models_form(form_class)

        return form_class

    def scaffold_list_form(self, validators=None):
        converter = self.model_field_converter(self.session, self.view)
        form_class = get_model_form(
            self.model,
            converter,
            base_class=self.view.base_form_class,
            only=self.view.column_editable_list,
            field_args=validators,
        )

        return form_class

    def get_list(self, search, filters, sort_field, sort_desc, page, page_size=None):
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

        self._apply_sorting(query, sort_field, sort_desc)

        # print(query)

        stmt = query.build()
        result = self.session.execute(stmt).scalars().all()

        return count, result

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

    def get_one(self, id):
        """Return a single model by its id.

        Args:
            id:
                Model id
        """
        if self._is_multiple_pk:
            id = tuple(id.split(","))
        return self.session.get(self.model, id)

    def create_model(self, form):
        """Create model from form.

        Args:
            form: Form instance
        """
        try:
            instance = self.model()
            form.populate_obj(instance)
            self.session.add(instance)
            self.session.commit()
            return instance
        except SQLAlchemyError:
            self.session.rollback()
            return None

    def update_model(self, form, model):
        """Update model from form.

        Args:
            form: Form instance
            model: Model instance
        """
        try:
            form.populate_obj(model)
            self.session.commit()
            return True
        except SQLAlchemyError:
            self.session.rollback()
            return False

    def delete_model(self, model) -> bool:
        try:
            self.session.delete(model)
            self.session.commit()
            return True
        except SQLAlchemyError:
            self.session.rollback()
            return False

    def delete_model_by_pk_ids(self, ids: list) -> int:
        """Delete multiple records by primary key.

        Return the number removed.
        """
        try:
            stmt = Query.delete_by_pk_ids(self.model, ids)
            result = self.session.execute(stmt)
            self.session.commit()
            return result.rowcount
        except SQLAlchemyError:
            self.session.rollback()
            raise

    def create_ajax_loader(self, name, options):
        attr = getattr(self.model, name, None)
        remote_model = attr.prop.mapper.class_
        return AjaxSqlaModelLoader(name, remote_model, self.session, **options)

    def scaffold_inline_models_form(self, form_class):
        """Contribute inline models to the form

        Args:
            form_class: Form class
        """
        default_converter = self.inline_model_converter(
            self.session, self.view, self.model_field_converter
        )

        for m in self.view.inline_models:
            if hasattr(m, "inline_model_converter"):
                custom_converter = m.inline_model_converter(
                    self.session, self, self.model_field_converter
                )
                form_class = custom_converter.contribute(self.model, form_class, m)
            else:
                form_class = default_converter.contribute(self.model, form_class, m)
        return form_class

    # --- Query --------------

    def _apply_search(self, query: Query, search):
        query.add_search_term(search, self.column_searchable_list)

    def _apply_filters(self, query: Query, filters):
        for idx, flt_name, value in filters:
            flt = self.view.get_filters()[idx]
            clean_value = flt.clean(value)
            flt.apply(query, clean_value)

    def _apply_sorting(self, query: Query, sort_column, sort_desc):
        if sort_column is not None:
            if sort_column in self.view.get_sortable_columns():
                sort_field = self.view.get_sortable_columns()[sort_column]
                if isinstance(sort_field, (list, tuple)):
                    for field_item in sort_field:
                        query.add_order_by(field_item, sort_desc)
                else:
                    query.add_order_by(sort_field, sort_desc)
        else:
            if default_order := self.view.get_default_order():
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

    def _normalize_inline_pk(self,value):
            if isinstance(value, (tuple, list)):
                return tuple(str(part) for part in value)
            return str(value)

    def _get_related_inline_object(self, parent, relationship_name, child_id):
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
