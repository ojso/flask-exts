from math import ceil

from flask import (
    abort,
    flash,
    get_flashed_messages,
    jsonify,
    redirect,
    request,
)
from flask_babel import gettext, ngettext

from ..exposer import expose_url
from .base import BaseModelView
from .type_formatters import BASE_FORMATTERS, DETAIL_FORMATTERS, EXPORT_FORMATTERS


class ModelView(BaseModelView):
    """Base admin view for model-backed resources.

    This class expects a standard model API with listing, retrieval, creation,
    update, deletion, and form scaffolding support. It does not assume a
    specific backend store, but it does require the implementation of the common
    model operations described by the admin layer.

    Typical subclass responsibilities include:

    1. Implementing data operations such as ``get_list`` and ``get_one``.
    2. Providing form generation via ``scaffold_form``.
    3. Defining column metadata and display configuration.

    The class is primarily responsible for route methods and view setup while
    the composed mixins supply the individual admin features.
    """

    def __init__(
        self,
        model,
        name=None,
        endpoint=None,
        url=None,
        static_folder=None,
    ):
        """
        Constructor.

        :param model:
            Model class
        :param name:
            View name. If not provided, will use the model class name
        :param endpoint:
            Base endpoint. If not provided, will use the model name.
        :param url:
            Base URL. If not provided, will use endpoint as a URL.
        :param static_folder:
            Static folder for the view. If not provided, will use the default static folder.
        """
        self.model = model

        if name is None:
            name = self._prettify_class_name(model.__name__)

        if endpoint is None:
            endpoint = self.model.__name__.lower()

        super().__init__(
            name,
            endpoint,
            url,
            static_folder,
        )

        self._init_view()

    def _init_view(self):
        """Initialize the list, sort, detail, export, and form metadata."""
        self._list_columns = self.get_list_columns()
        self._sortable_columns = self.get_sortable_columns()
        self._details_columns = self.get_details_columns()
        self._export_columns = self.get_export_columns()

        if hasattr(self, "init_actions"):
            self.init_actions()
        if hasattr(self, "init_row_actions"):
            self.init_row_actions()
        if hasattr(self, "init_filters"):
            self.init_filters()

        self._init_forms()

        if self.column_formatters_export is None:
            self.column_formatters_export = self.column_formatters

        if self.column_formatters_detail is None:
            self.column_formatters_detail = self.column_formatters

        if self.column_type_formatters is None:
            self.column_type_formatters = dict(BASE_FORMATTERS)

        if self.column_type_formatters_export is None:
            self.column_type_formatters_export = dict(EXPORT_FORMATTERS)

        if self.column_type_formatters_detail is None:
            self.column_type_formatters_detail = dict(DETAIL_FORMATTERS)

        if self.column_descriptions is None:
            self.column_descriptions = dict()

    def _init_forms(self):
        """Initialize the form classes used by the view."""
        self._form_ajax_refs = self._process_ajax_references()

        if self.form_widget_args is None:
            self.form_widget_args = {}

        self._create_form_class = self.get_create_form()
        self._edit_form_class = self.get_edit_form()
        self._delete_form_class = self.get_delete_form()

        if self.column_editable_list:
            self._list_form_class = self.get_list_form()

    def is_editable(self, name: str) -> bool:
        """Return whether the given column is editable.

        Args:
            name: Column name.

        Returns:
            bool: ``True`` when the column is editable.
        """
        return (
            self.can_edit
            and self.column_editable_list is not None
            and name in self.column_editable_list
        )

    def is_action_allowed(self, name: str) -> bool:
        """Return whether an action is allowed for the current view."""
        if name == "delete" and not self.can_delete:
            return False
        return (
            super().is_action_allowed(name)
            if hasattr(super(), "is_action_allowed")
            else True
        )

    def _process_ajax_references(self):
        """Process AJAX reference configuration into model loaders."""
        result = {}

        if self.form_ajax_refs:
            from .ajax import AjaxModelLoader

            for name, options in self.form_ajax_refs.items():
                if isinstance(options, AjaxModelLoader):
                    result[name] = options
                else:
                    result[name] = self._create_ajax_loader(name, options)
        return result

    def _create_ajax_loader(self, name, options):
        """Create an AJAX model loader for an AJAX-backed form field."""
        raise NotImplementedError()

    def get_redirect_target(self, param_name="url", endpoint=".index_view"):
        """Return the target URL used for redirects."""
        return request.values.get(param_name) or self.get_url(endpoint)

    # Route methods.

    @expose_url("/")
    def index_view(self):
        """Index view"""

        # Grab parameters from URL
        view_args = self._get_list_args()

        sort_column = self._get_column_by_idx(view_args.sort)
        if sort_column is not None:
            sort_column = sort_column[0]

        page_size = self.get_safe_page_size(view_args.page_size)

        count, data = self.get_list(
            view_args.page,
            sort_column,
            view_args.sort_desc,
            view_args.search,
            view_args.filters,
            page_size=page_size,
        )

        if count is not None and page_size:
            num_pages = int(ceil(count / float(page_size)))
        elif not page_size:
            num_pages = 0
        else:
            num_pages = None
        def pager_url(p):
            # Do not add page number if it is first page
            if p == 0:
                p = None
            return self._get_list_url(view_args.clone(page=p))

        def sort_url(column, invert=False, desc=None):
            if not desc and invert and not view_args.sort_desc:
                desc = 1
            return self._get_list_url(view_args.clone(sort=column, sort_desc=desc))

        def page_size_url(s):
            return self._get_list_url(view_args.clone(page_size=s))

        clear_search_url = self._get_list_url(
            view_args.clone(
                page=0,
                sort=view_args.sort,
                sort_desc=view_args.sort_desc,
                search=None,
                filters=None,
            )
        )

        return self.render(
            self.list_template,
            data=data,
            # list
            list_columns=self._list_columns,
            sortable_columns=self._sortable_columns,
            editable_columns=self.column_editable_list,
            # Pagination
            count=count,
            pager_url=pager_url,
            num_pages=num_pages,
            page_size_url=page_size_url,
            page=view_args.page,
            page_size=page_size,
            default_page_size=self.page_size,
            # sort
            sort_column=view_args.sort,
            sort_desc=view_args.sort_desc,
            sort_url=sort_url,
            # search
            clear_search_url=clear_search_url,
            search=view_args.search,
            # filter
            active_filters=view_args.filters,
            filter_args=(
                self.get_active_filters_kwargs(view_args.filters)
                if hasattr(self, "get_active_filters_kwargs")
                else {}
            ),
            # misc
            return_url=self._get_list_url(view_args),
            extra_args=view_args.extra_args,
        )

    @expose_url("/new/", methods=("GET", "POST"))
    def create_view(self):
        """Create model view"""
        return_url = self.get_redirect_target()

        if not self.can_create:
            return redirect(return_url)

        form = self.create_form()

        if form.validate_on_submit():
            model = self.create_model(form)
            if model:
                flash(gettext("Record was successfully created."), "success")
                if "_add_another" in request.form:
                    return redirect(request.url)
                elif "_continue_editing" in request.form:
                    if model is not True:
                        url = self.get_url(
                            ".edit_view", id=self.get_pk_value(model), url=return_url
                        )
                    else:
                        url = return_url
                    return redirect(url)
                else:
                    return redirect(self.get_save_return_url(model, is_created=True))

        form_opts = dict(widget_args=self.form_widget_args)

        if self.create_modal and request.args.get("modal"):
            template = self.create_modal_template
        else:
            template = self.create_template

        return self.render(
            template, form=form, form_opts=form_opts, return_url=return_url
        )

    @expose_url("/edit/", methods=("GET", "POST"))
    def edit_view(self):
        """Edit model view"""
        return_url = self.get_redirect_target()

        if not self.can_edit:
            return redirect(return_url)

        id = request.args.get("id")

        if id is None:
            return redirect(return_url)

        model = self.get_one(id)

        if model is None:
            flash(gettext("Record does not exist."), "error")
            return redirect(return_url)

        form = self._edit_form_class(obj=model)

        if form.validate_on_submit():
            if self.update_model(form, model):
                flash(gettext("Record was successfully saved."), "success")
                if "_add_another" in request.form:
                    return redirect(self.get_url(".create_view", url=return_url))
                elif "_continue_editing" in request.form:
                    return redirect(
                        self.get_url(".edit_view", id=self.get_pk_value(model))
                    )
                else:
                    return redirect(self.get_save_return_url(model, is_created=False))

        form_opts = dict(widget_args=self.form_widget_args)

        if self.edit_modal and request.args.get("modal"):
            template = self.edit_modal_template
        else:
            template = self.edit_template

        return self.render(
            template, model=model, form=form, form_opts=form_opts, return_url=return_url
        )

    @expose_url("/details/")
    def details_view(self):
        """Details model view"""
        return_url = self.get_redirect_target()

        id = request.args.get("id")

        if id is None:
            return redirect(return_url)

        model = self.get_one(id)

        if model is None:
            flash(gettext("Record does not exist."), "error")
            return redirect(return_url)

        if self.details_modal and request.args.get("modal"):
            template = self.details_modal_template
        else:
            template = self.details_template

        return self.render(
            template,
            model=model,
            details_columns=self._details_columns,
            return_url=return_url,
        )

    @expose_url("/delete/", methods=("POST",))
    def delete_view(self):
        """Delete model view. Only POST method is allowed."""
        return_url = self.get_redirect_target()
        if not self.can_delete:
            return redirect(return_url)

        form = self.delete_form()
        if form.validate():
            id = form.id.data
            model = self.get_one(id)
            if model is None:
                flash(gettext("Record does not exist."), "error")
                return redirect(return_url)

            if self.delete_model(model):
                count = 1
                flash(
                    ngettext(
                        "Record was successfully deleted.",
                        "%(count)s records were successfully deleted.",
                        count,
                        count=count,
                    ),
                    "success",
                )
                return redirect(return_url)
        else:
            if hasattr(form, "flash_errors"):
                form.flash_errors(message="Failed to delete record. %(error)s")

        return redirect(return_url)

    @expose_url("/ajax/lookup/")
    def ajax_lookup(self):
        """AJAX lookup"""
        name = request.args.get("name")
        query = request.args.get("query")
        offset = request.args.get("offset", type=int)
        limit = request.args.get("limit", 10, type=int)
        loader = self._form_ajax_refs.get(name)
        if not loader:
            abort(404)

        data = [loader.format(m) for m in loader.get_list(query, offset, limit)]
        return jsonify(data)

    @expose_url("/ajax/update/", methods=("POST",))
    def ajax_update(self):
        """Ajax update. Edits a single column of a record in list view."""

        if not self.column_editable_list:
            abort(404)
        if not request.is_json:
            abort(404)
            
        json_data = request.get_json()

        form = self.list_form()

        # Delete non-submitted fields to prevent validation issues.
        for field in list(form):
            if field.name in json_data or field.name == "csrf_token":
                pass
            else:
                form.__delitem__(field.name)

        if form.validate_on_submit():
            pk = form.pk.data
            record = self.get_one(pk)

            if record is None:
                return gettext("Record does not exist."), 500

            if self.update_model(form, record):
                return gettext("Record was successfully saved.")
            else:
                msgs = ", ".join([msg for msg in get_flashed_messages()])
                return gettext("Failed to update record. %(error)s", error=msgs), 500
        else:
            for field in form:
                for error in field.errors:
                    if isinstance(error, list):
                        return (
                            gettext(
                                "Failed to update record. %(error)s",
                                error=", ".join(error),
                            ),
                            500,
                        )
                    else:
                        return (
                            gettext("Failed to update record. %(error)s", error=error),
                            500,
                        )

        return gettext("Validation failed."), 400
