"""Data backend protocol for model-backed admin views.

``ModelView`` handle everything that is independent of where the data actually
lives: routing, URL/pagination argument parsing, column/label metadata
plumbing, template rendering, form field wrapping.

Everything that *does* depend on the data source -- how records are listed,
sorted, filtered, fetched, created, updated, deleted, and how a form class is
generated from the underlying schema -- is delegated to a ``DataBackend``
instance that the view holds via composition instead of inheriting from a
backend-specific base class.

A concrete backend (e.g. :class:`~flask_exts.admin.sqla.backend.SqlaBackend`)
is free to read public, view-level configuration (such as
``view.column_searchable_list`` or ``view._filters``) through the ``view``
reference it is constructed with. This keeps state that is inherently a
"view/request" concern -- parsed filter objects, sortable-column mappings --
in one place (``ModelView``) rather than duplicating it, while still letting
the backend use it to do its job.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from .view import ModelView


class DataBackend(ABC):
    """Protocol for a pluggable data source behind a :class:`ModelView`.

    Implementations hold whatever resource they need (a SQLAlchemy session,
    a path to a JSON file, a filesystem root directory, ...) and translate
    the view's generic requests into operations on that resource.
    """

    def __init__(self, model, view: ModelView):
        self.model = model
        self.view = view

    # --- Column / sortable-column / filter / form metadata -------------

    @abstractmethod
    def scaffold_list_columns(self) -> list[str]:
        """Return the list of model field names to display in list views."""

    @abstractmethod
    def scaffold_sortable_columns(self) -> dict[str, str | list[str]]:
        """Return a mapping of sortable column name to the field(s) used to sort by."""

    @abstractmethod
    def scaffold_filter(self, column_path: str) -> list | None:
        """Return the filter objects available for the given column path."""

    @abstractmethod
    def scaffold_form(self, form_type: str | None = None) -> type:
        """Return a form class for creating/editing a record."""

    @abstractmethod
    def scaffold_list_form(self, validators=None) -> type:
        """Return a form class for inline editing from the list view."""

    # --- Reads -----------------------------------------------------------

    @abstractmethod
    def get_list(
        self,
        search: str | None,
        filters: list[tuple] | None,
        sort_field: str | None,
        sort_desc: bool | None,
        page: int | None,
        page_size: int | None = None,
    ) -> tuple[int, list]:
        """Get list of models.

        Args:
            search:
                Search query
            filters:
                List of filter tuples
            sort_column:
                Sort column name
            sort_desc:
                Descending or ascending sort
            page:
                Page number
            page_size:
                Number of results. Defaults to ModelView's page_size. Can be
                overriden to change the page_size limit. Removing the page_size
                limit requires setting page_size to 0 or False.

        Return:
            ``(count, rows)`` for one page of results.
        """

    @abstractmethod
    def get_one(self, id):
        """Return a single record by primary key, or ``None``."""

    @abstractmethod
    def get_pk_value(self, obj: Any) -> str:
        """Return the string representation of a record's primary key."""

    # --- Writes ------------------------------------------------------------

    @abstractmethod
    def create_model(self, form) -> Any:
        """Create a record from a validated form. Return the new record, or
        ``None`` on failure (implementations handle their own flash
        messaging, matching the existing convention)."""

    @abstractmethod
    def update_model(self, form, model: Any) -> bool:
        """Update ``model`` from a validated form. Return success as a bool."""

    @abstractmethod
    def delete_model(self, model: Any) -> bool:
        """Delete a model instance.

        Args:
            model: Model instance to remove.

        Returns:
            bool: ``True`` if the delete operation succeeded, otherwise ``False``.
        """

    @abstractmethod
    def delete_model_by_pk_ids(self, ids: list) -> int:
        """Delete multiple records by primary key. Return the number removed."""

    # --- Optional: AJAX foreign-key lookups --------------------------------

    def create_ajax_loader(self, name: str, options: dict):
        """Create an AJAX loader for a ``ajax_refs`` field.

        Not every backend has a notion of foreign-key lookups (a JSON-file
        or filesystem backend most likely doesn't), so this has a default
        "unsupported" implementation rather than being an abstractmethod --
        only backends that opt into ``ajax_refs`` need to override it.
        """
