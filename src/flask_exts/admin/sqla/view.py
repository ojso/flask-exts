from typing import Optional, Dict, List, Tuple
from flask import flash
from flask_babel import gettext
from sqlalchemy import inspect
from ...datastore.sqla import db
from ..model.view import ModelView
from . import form
from .filter import FilterConverter
from .ajax import create_ajax_loader
from .typefmt import DEFAULT_FORMATTERS
from .query import Query


class SqlaModelView(ModelView):
    """
    SQLAlchemy model view
    """

    model_form_converter = form.FormConverter
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

        self._primary_key = Query.get_model_primary_key(self.model)
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
        value = Query.get_instance_identity(instance)
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
        columns = dict()
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

        column_type = Query.get_model_column_type(self.model, column_path)

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

        return self.create_editable_list_form(form_class, widget)

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
                for sort_field, sort_desc in default_order:
                    query.add_order_by(sort_field, sort_desc)

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

        :param id:
            Model id
        """
        if self._is_multiple_pk:
            id = tuple(id.split(","))
        return self.session.get(self.model, id)

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

        :param form:
            Form instance
        :param model:
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
        except Exception as ex:
            self.session.rollback()
            raise ex
