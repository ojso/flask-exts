from typing import Optional, Dict, List, Tuple
from flask import flash
from flask_babel import gettext, ngettext, lazy_gettext
from sqlalchemy.sql import select
from sqlalchemy.orm.attributes import InstrumentedAttribute
from sqlalchemy.orm import joinedload, selectinload, aliased
from sqlalchemy.sql.expression import desc
from sqlalchemy import Boolean, func, or_
from sqlalchemy.exc import IntegrityError
from sqlalchemy.sql.expression import cast
from sqlalchemy import Unicode
from ...datastore.sqla import db
from ...datastore.sqla.utils import is_relationship
from ...datastore.sqla.utils import get_field_with_path
from ...datastore.sqla.utils import parse_like_term
from ..model.view import ModelView
from ..model.form import create_editable_list_form
from . import form
from .filter import BaseSQLAFilter
from .filter import FilterConverter
from .ajax import create_ajax_loader
from .typefmt import DEFAULT_FORMATTERS
from ...datastore.sqla.utils import get_model_mapper
from ...datastore.sqla.utils import get_primary_key
from ...datastore.sqla.utils import get_identity
from ...datastore.sqla.stmt import stmt_delete_by_pk_ids


def need_join(model, table):
    from sqlalchemy import inspect

    mapper = inspect(model)
    return table not in mapper.tables


class SqlaModelView(ModelView):
    """
    SQLAlchemy model view
    """

    column_searchable_list = None
    """
        Collection of the searchable columns.

        Example::

            class MyModelView(ModelView):
                column_searchable_list = ('name', 'email')

        You can also pass columns::

            class MyModelView(ModelView):
                column_searchable_list = (User.name, User.email)

        The following search rules apply:

        - If you enter ``ZZZ`` in the UI search field, it will generate ``ILIKE '%ZZZ%'``
          statement against searchable columns.

        - If you enter multiple words, each word will be searched separately, but
          only rows that contain all words will be displayed. For example, searching
          for ``abc def`` will find all rows that contain ``abc`` and ``def`` in one or
          more columns.

        - If you prefix your search term with ``^``, it will find all rows
          that start with ``^``. So, if you entered ``^ZZZ`` then ``ILIKE 'ZZZ%'`` will be used.

        - If you prefix your search term with ``=``, it will perform an exact match.
          For example, if you entered ``=ZZZ``, the statement ``ILIKE 'ZZZ'`` will be used.
    """

    column_filters = None
    """
        Collection of the column filters.

        Can contain either field names or instances of
        :class:`.sqla.filters.BaseSQLAFilter` classes.

        Filters will be grouped by name when displayed in the drop-down.

        For example::

            class MyModelView(BaseModelView):
                column_filters = ('user', 'email')

        or::

            from .sqla.filters import BooleanEqualFilter

            class MyModelView(BaseModelView):
                column_filters = (BooleanEqualFilter(column=User.name, name='Name'),)

        or::

            from .sqla.filters import BaseSQLAFilter

            class FilterLastNameBrown(BaseSQLAFilter):
                def apply(self, query, value, alias=None):
                    if value == '1':
                        return query.filter(self.column == "Brown")
                    else:
                        return query.filter(self.column != "Brown")

                def operation(self):
                    return 'is Brown'

            class MyModelView(BaseModelView):
                column_filters = [
                    FilterLastNameBrown(
                        User.last_name, 'Last Name', options=(('1', 'Yes'), ('0', 'No'))
                    )
                ]
    """

    model_form_converter = form.AdminModelConverter
    """
        Model form conversion class. Use this to implement custom field conversion logic.

        For example::

            class MyModelConverter(AdminModelConverter):
                pass


            class MyAdminView(ModelView):
                model_form_converter = MyModelConverter
    """

    inline_model_form_converter = form.InlineModelConverter
    """
        Inline model conversion class. If you need some kind of post-processing for inline
        forms, you can customize behavior by doing something like this::

            class MyInlineModelConverter(InlineModelConverter):
                def post_process(self, form_class, info):
                    form_class.value = wtf.StringField('value')
                    return form_class

            class MyAdminView(ModelView):
                inline_model_form_converter = MyInlineModelConverter
    """

    filter_converter = FilterConverter()
    """
        Field to filter converter.

        Override this attribute to use non-default converter.
    """

    inline_models = None
    """
        Inline related-model editing for models with parent-child relations.

        Accepts enumerable with one of the following possible values:

        1. Child model class::

            class MyModelView(ModelView):
                inline_models = (Post,)

        2. Child model class and additional options::

            class MyModelView(ModelView):
                inline_models = [(Post, dict(form_columns=['title']))]

        3. Django-like ``InlineFormAdmin`` class instance::

            from .model.form import InlineFormAdmin

            class MyInlineModelForm(InlineFormAdmin):
                form_columns = ('title', 'date')

            class MyModelView(ModelView):
                inline_models = (MyInlineModelForm(MyInlineModel),)

        You can customize the generated field name by:

        1. Using the `form_name` property as a key to the options dictionary::

            class MyModelView(ModelView):
                inline_models = ((Post, dict(form_label='Hello')))

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
        To achieve this, you need to install special ``inline_converter``
        for your model::

            from .sqla.form import InlineOneToOneModelConverter

            class MyInlineModelForm(InlineFormAdmin):
                form_columns = ('title', 'date')
                inline_converter = InlineOneToOneModelConverter

            class MyModelView(ModelView):
                inline_models = (MyInlineModelForm(MyInlineModel),)
    """

    column_type_formatters = DEFAULT_FORMATTERS

    form_choices: Optional[Dict[str, List[Tuple[str, str]]]] = None
    """
        Map choices to form fields

        Example::

            class MyModelView(BaseModelView):
                form_choices = {'my_form_field': [
                    ('db_value', 'display_value'),
                ]}
    """

    form_optional_types = (Boolean,)
    """
        List of field types that should be optional if column is not nullable.

        Example::

            class MyModelView(BaseModelView):
                form_optional_types = (Boolean, Unicode)
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

        :param model:
            Model class
        :param session:
            SQLAlchemy session
        :param name:
            View name. If not set, defaults to the model name
        :param endpoint:
            Endpoint name. If not set, defaults to the model name
        :param url:
            Base URL. If not set, defaults to '/admin/' + endpoint
        """
        # set db.session as default session
        self.session = session if session is not None else db.session

        self._search_fields = None
        self._filter_joins = dict()
        self._sortable_joins = dict()

        if self.form_choices is None:
            self.form_choices = {}

        super().__init__(
            model,
            name,
            endpoint,
            url,
            static_folder,
        )

        self._primary_key = get_primary_key(self.model)
        self._is_multiple_pk = isinstance(self._primary_key, tuple)

        if self._primary_key is None:
            raise Exception("Model %s does not have primary key." % self.model.__name__)

        self._auto_joins = self._init_auto_joins()

        # print(self.model)
        # print(self._list_columns)
        # print(
        #     [r.key for r in self._auto_joins[0]], [r.key for r in self._auto_joins[1]]
        # )

    # Error handler
    def handle_view_exception(self, exc):
        if isinstance(exc, IntegrityError):
            flash(gettext("Integrity error. %(message)s", message=str(exc)), "error")
            return True

        return super().handle_view_exception(exc)

    def _init_auto_joins(self):
        """
        Return a list of joined tables by going through the displayed columns.
        """
        manytoone_relations = set()
        manytomany_relations = set()
        list_columns = set()

        for p in get_model_mapper(self.model).attrs:
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
        value = get_identity(instance)
        if isinstance(value, tuple):
            return ",".join([str(v) for v in value])
        else:
            return str(value)

    def _apply_path_joins(self, query, joins, path, isouter=True):
        """
        Apply join path to the query.

        :param query:
            Query to add joins to
        :param joins:
            List of current joins. Used to avoid joining on same relationship more than once
        :param path:
            Path to be joined
        :param isouter:
            if True, generate LEFT OUTER join, otherwise generate INNER JOIN
        """
        last = None

        if path:
            for item in path:
                key = (isouter, item)
                alias = joins.get(key)

                if key not in joins:
                    alias = aliased(item.property.mapper.class_)
                    fn = query.outerjoin if isouter else query.join

                    if last is None:
                        query = fn(alias, item)
                    else:
                        prop = getattr(last, item.key)
                        query = fn(alias, prop)

                    joins[key] = alias

                last = alias

        return query, joins, last

    def scaffold_list_columns(self):
        """
        Return a list of columns from the model.
        """
        columns = []

        for p in get_model_mapper(self.model).attrs:
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
        columns = dict()

        for p in get_model_mapper(self.model).attrs:
            if hasattr(p, "columns"):
                if len(p.columns) > 1:
                    # Multi-column properties are not supported
                    continue
                column = p.columns[0]
                # Can't sort on primary or foreign keys by default
                if column.foreign_keys:
                    continue
                columns[p.key] = column

        return columns

    def get_sortable_columns(self):
        """
        Returns a dictionary of the sortable columns. Key is a model
        field name and value is sort column (for example - attribute).

        If `column_sortable_list` is set, will use it. Otherwise, will call
        `scaffold_sortable_columns` to get them from the model.
        """
        self._sortable_joins = dict()

        if self.column_sortable_list is None:
            return self.scaffold_sortable_columns()
        else:
            result = dict()

            for c in self.column_sortable_list:
                if isinstance(c, tuple):
                    if isinstance(c[1], tuple):
                        column, path = [], []
                        for item in c[1]:
                            column_item, path_item = get_field_with_path(
                                self.model, item
                            )
                            column.append(column_item)
                            path.append(path_item)
                        column_name = c[0]
                    else:
                        column, path = get_field_with_path(self.model, c[1])
                        column_name = c[0]
                else:
                    column, path = get_field_with_path(self.model, c)
                    column_name = str(c)

                if path and (hasattr(path[0], "property") or isinstance(path[0], list)):
                    self._sortable_joins[column_name] = path
                elif path:
                    raise Exception(
                        "For sorting columns in a related table, "
                        "column_sortable_list requires a string "
                        "like '<relation name>.<column name>'. "
                        "Failed on: {0}".format(c)
                    )
                else:
                    # column is in same table, use only model attribute name
                    if getattr(column, "key", None) is not None:
                        column_name = column.key

                # column_name must match column_name used in `get_list_columns`
                result[column_name] = column

            return result

    def get_column_names(self, columns):
        """
        Returns a list of tuples with the model field name and formatted
        field name.

        Overridden to handle special columns like InstrumentedAttribute.

        :param columns:
            List of columns to include in the results.
        """
        formatted_columns = []
        for c in columns:
            try:
                column, path = get_field_with_path(self.model, c)

                if path:
                    # column is a relation (InstrumentedAttribute), use full path
                    column_name = str(c)
                else:
                    # column is in same table, use only model attribute name
                    if getattr(column, "key", None) is not None:
                        column_name = column.key
                    else:
                        column_name = str(c)
            except AttributeError:
                # TODO: See ticket #1299 - allow virtual columns. Probably figure out
                # better way to handle it. For now just assume if column was not found - it
                # is virtual and there's column formatter for it.
                column_name = str(c)

            visible_name = self.get_column_label(column_name)

            # column_name must match column_name in `get_sortable_columns`
            formatted_columns.append((column_name, visible_name))

        return formatted_columns

    def init_search(self):
        """
        Initialize search. Returns `True` if search is supported for this
        view.

        For SQLAlchemy, this will initialize internal fields: list of
        column objects used for filtering, etc.
        """
        if self.column_searchable_list:
            self._search_fields = []

            for name in self.column_searchable_list:
                attr, joins = get_field_with_path(self.model, name)

                if not attr:
                    raise Exception("Failed to find field for search field: %s" % name)

                self._search_fields.append((attr, joins))

        return bool(self.column_searchable_list)

    def search_placeholder(self):
        """
        Return search placeholder.

        For example, if set column_labels and column_searchable_list:

        class MyModelView(BaseModelView):
            column_labels = dict(name='Name', last_name='Last Name')
            column_searchable_list = ('name', 'last_name')

        placeholder is: "Name, Last Name"
        """
        if not self.column_searchable_list:
            return None

        placeholders = []

        for searchable in self.column_searchable_list:
            if isinstance(searchable, InstrumentedAttribute):
                placeholders.append(
                    str(self.column_labels.get(searchable.key, searchable.key))
                )
            else:
                placeholders.append(str(self.column_labels.get(searchable, searchable)))

        return ", ".join(placeholders)

    def scaffold_filters(self, name):
        """
        Return list of enabled filters
        """

        attr, joins = get_field_with_path(self.model, name)

        if attr is None:
            raise Exception("Failed to find field for filter: %s" % name)

        if is_relationship(attr):
            raise Exception("Relationship can not be a filter field: %s" % name)

        column = attr

        if self.column_labels and name in self.column_labels:
            visible_name = self.column_labels[name]
        else:
            visible_name = name.replace(".", " / ")

        flt = self.filter_converter.convert(
            type(column.type).__name__,
            column,
            visible_name,
            options=self.column_choices.get(name),
        )

        if joins:
            self._filter_joins[name] = joins

        return flt

    def handle_filter(self, filter):
        if isinstance(filter, BaseSQLAFilter):
            column = filter.column

            if isinstance(column, InstrumentedAttribute) and need_join(
                self.model, column.table
            ):
                self._filter_joins[column] = [column.table]

        return filter

    def scaffold_form(self):
        """
        Create form from the model.
        """
        converter = self.model_form_converter(self.session, self)
        form_class = form.get_form(
            self.model,
            converter,
            base_class=self.form_base_class,
            only=self.form_columns,
            exclude=self.form_excluded_columns,
            field_args=self.form_args,
            extra_fields=self.form_extra_fields,
        )

        if self.inline_models:
            form_class = self.scaffold_inline_form_models(form_class)

        return form_class

    def scaffold_list_form(self, widget=None, validators=None):
        """
        Create form for the `index_view` using only the columns from
        `self.column_editable_list`.

        :param widget:
            WTForms widget class. Defaults to `XEditableWidget`.
        :param validators:
            `form_args` dict with only validators
            {'name': {'validators': [required()]}}
        """
        converter = self.model_form_converter(self.session, self)
        form_class = form.get_form(
            self.model,
            converter,
            base_class=self.form_base_class,
            only=self.column_editable_list,
            field_args=validators,
        )

        return create_editable_list_form(self.form_base_class, form_class, widget)

    def scaffold_inline_form_models(self, form_class):
        """
        Contribute inline models to the form

        :param form_class:
            Form class
        """
        default_converter = self.inline_model_form_converter(
            self.session, self, self.model_form_converter
        )

        for m in self.inline_models:
            if not hasattr(m, "inline_converter"):
                form_class = default_converter.contribute(self.model, form_class, m)
                continue

            custom_converter = m.inline_converter(
                self.session, self, self.model_form_converter
            )
            form_class = custom_converter.contribute(self.model, form_class, m)
        return form_class

    # AJAX foreignkey support
    def _create_ajax_loader(self, name, options):
        return create_ajax_loader(self.model, self.session, name, name, options)

    def _order_by(self, query, joins, sort_joins, sort_field, sort_desc):
        """
        Apply order_by to the query

        :param query:
            Query
        :pram joins:
            Current joins
        :param sort_joins:
            Sort joins (properties or tables)
        :param sort_field:
            Sort field
        :param sort_desc:
            Ascending or descending
        """
        if sort_field is not None:
            query, joins, alias = self._apply_path_joins(query, joins, sort_joins)

            column = sort_field if alias is None else getattr(alias, sort_field.key)

            if sort_desc:
                query = query.order_by(desc(column))
            else:
                query = query.order_by(column)

        return query, joins

    def _get_default_order(self):
        order = super()._get_default_order()
        for field, direction in order or []:
            attr, joins = get_field_with_path(self.model, field)
            yield attr, joins, direction

    def _apply_sorting(self, query, joins, sort_column, sort_desc):
        if sort_column is not None:
            if sort_column in self._sortable_columns:
                sort_field = self._sortable_columns[sort_column]
                sort_joins = self._sortable_joins.get(sort_column)

                if isinstance(sort_field, list):
                    for field_item, join_item in zip(sort_field, sort_joins):
                        query, joins = self._order_by(
                            query, joins, join_item, field_item, sort_desc
                        )
                else:
                    query, joins = self._order_by(
                        query, joins, sort_joins, sort_field, sort_desc
                    )
        else:
            order = self._get_default_order()
            for sort_field, sort_joins, sort_desc in order:
                query, joins = self._order_by(
                    query, joins, sort_joins, sort_field, sort_desc
                )

        return query, joins

    def _apply_search(self, query, count_query, joins, count_joins, search):
        """
        Apply search to a query.
        """
        terms = search.split(" ")

        for term in terms:
            if not term:
                continue

            stmt = parse_like_term(term)

            filter_stmt = []
            count_filter_stmt = []

            for field, path in self._search_fields:
                query, joins, alias = self._apply_path_joins(query, joins, path)
                count_alias = None

                if count_query is not None:
                    count_query, count_joins, count_alias = self._apply_path_joins(
                        count_query, count_joins, path
                    )

                column = field if alias is None else getattr(alias, field.key)
                filter_stmt.append(cast(column, Unicode).ilike(stmt))

                if count_filter_stmt is not None:
                    column = (
                        field
                        if count_alias is None
                        else getattr(count_alias, field.key)
                    )
                    count_filter_stmt.append(cast(column, Unicode).ilike(stmt))

            query = query.filter(or_(*filter_stmt))

            if count_query is not None:
                count_query = count_query.filter(or_(*count_filter_stmt))

        return query, count_query, joins, count_joins

    def _apply_filters(self, query, count_query, joins, count_joins, filters):
        for idx, flt_name, value in filters:
            flt = self._filters[idx]

            alias = None
            count_alias = None

            if isinstance(flt, BaseSQLAFilter):
                # If no key_name is specified, use filter column as filter key
                filter_key = flt.key_name or flt.column
                path = self._filter_joins.get(filter_key, [])

                query, joins, alias = self._apply_path_joins(query, joins, path)

                if count_query is not None:
                    count_query, count_joins, count_alias = self._apply_path_joins(
                        count_query, count_joins, path
                    )

            clean_value = flt.clean(value)
            query = flt.apply(query, clean_value, alias)

            if count_query is not None:
                count_query = flt.apply(count_query, clean_value, count_alias)

        return query, count_query, joins, count_joins

    def _apply_pagination(self, query, page, page_size):
        if page_size is None:
            page_size = self.page_size

        if page_size:
            query = query.limit(page_size)

        if page and page_size:
            query = query.offset(page * page_size)

        return query

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

        :param page:
            Page number
        :param sort_column:
            Sort column name
        :param sort_desc:
            Descending or ascending sort
        :param search:
            Search query
        :param execute:
            Execute query immediately? Default is `True`
        :param filters:
            List of filter tuples
        :param page_size:
            Number of results. Defaults to ModelView's page_size. Can be
            overriden to change the page_size limit. Removing the page_size
            limit requires setting page_size to 0 or False.
        """

        # Will contain join paths with optional aliased object
        joins = {}
        count_joins = {}

        query = select(self.model)
        count_query = select(func.count()).select_from(self.model)

        # Apply search criteria
        if self._search_supported and search:
            query, count_query, joins, count_joins = self._apply_search(
                query, count_query, joins, count_joins, search
            )

        # Apply filters
        if filters and self._filters:
            query, count_query, joins, count_joins = self._apply_filters(
                query, count_query, joins, count_joins, filters
            )

        # Calculate number of rows if necessary
        count = self.session.execute(count_query).scalar()

        # Auto join
        if joinedloads := self._auto_joins[0]:
            query = query.options(*[joinedload(j) for j in joinedloads])
        if selectinloads := self._auto_joins[1]:
            query = query.options(*[selectinload(j) for j in selectinloads])

        # Sorting
        query, joins = self._apply_sorting(query, joins, sort_column, sort_desc)

        # Pagination
        query = self._apply_pagination(query, page, page_size)

        result = self.session.execute(query).scalars().all()

        return count, result

    def get_one(self, id):
        """
        Return a single model by its id.

        :param id:
            Model id
        """
        if self._is_multiple_pk:
            id = tuple(id.split(","))
        return self.session.get(self.model, id)

    # Model handlers
    def create_model(self, form):
        """
        Create model from form.

        :param form:
            Form instance
        """
        try:
            instance = self.model()
            form.populate_obj(instance)
            self.session.add(instance)
            self._on_model_change(form, instance, True)
            self.session.commit()
        except Exception as ex:
            if not self.handle_view_exception(ex):
                flash(
                    gettext("Failed to create record. %(error)s", error=str(ex)),
                    "error",
                )

            self.session.rollback()

            return False
        else:
            self.after_model_change(form, instance, True)

        return instance

    def update_model(self, form, model):
        """
        Update model from form.

        :param form:
            Form instance
        :param model:
            Model instance
        """
        try:
            form.populate_obj(model)
            self._on_model_change(form, model, False)
            self.session.commit()
        except Exception as ex:
            if not self.handle_view_exception(ex):
                flash(
                    gettext("Failed to update record. %(error)s", error=str(ex)),
                    "error",
                )

            self.session.rollback()

            return False
        else:
            self.after_model_change(form, model, False)

        return True

    def delete_model(self, model):
        try:
            self.session.delete(model)
            self.session.commit()
            return True
        except Exception as ex:
            if not self.handle_view_exception(ex):
                flash(
                    gettext("Failed to delete record. %(error)s", error=str(ex)),
                    "error",
                )

            self.session.rollback()
            return False

    def delete_models_by_pk_ids(self, ids: list):
        try:
            stmt = stmt_delete_by_pk_ids(self.model, ids)
            result = self.session.execute(stmt)
            self.session.commit()
            return result.rowcount
        except Exception as ex:
            self.session.rollback()
            raise ex
