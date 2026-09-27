from typing import Optional, List, Tuple, Any
import csv
import mimetypes
import tablib
from flask import Response
from flask import redirect
from flask import flash
from flask import stream_with_context
from flask_babel import gettext
from werkzeug.utils import secure_filename
from ...exposer import expose_url


class ExportOperationsMixin:
    """Mixin for exporting model data in tabular formats."""

    can_export: bool = False
    """Whether export is enabled for the current view."""

    export_max_rows: int = 0
    """
        Maximum number of rows allowed for export.

        Unlimited by default. Uses `page_size` if set to `None`.
    """

    export_types: List[str] = ["csv"]
    """
        A list of available export filetypes. `csv` only is default, but any
        filetypes supported by tablib can be used.

        Check tablib for https://tablib.readthedocs.io/en/stable/formats.html
        for supported types.
    """

    def _export_data(self) -> Tuple[Optional[int], List[Any]]:
        """Return the rows to be exported.

        The method validates export formatters and then requests the filtered,
        sorted, and paginated data set needed for the export.

        Returns:
            Tuple[Optional[int], List[Any]]: ``(count, rows)``.

        Raises:
            NotImplementedError: If unsupported macros are used in export
                formatters.
        """
        for col, func in (self.column_formatters_export or {}).items():
            if col not in [col for col, _ in self._export_columns]:
                continue

            if func.__name__ == "inner":
                raise NotImplementedError(
                    "Macros are not implemented in export. Exclude column in"
                    " column_formatters_export, column_export_list. "
                    "Column: %s" % (col,)
                )

        view_args = self._get_list_args()
        sort_column = self._get_column_by_idx(view_args.sort)
        if sort_column is not None:
            sort_column = sort_column[0]

        count, data = self.get_list(
            0,
            sort_column,
            view_args.sort_desc,
            view_args.search,
            view_args.filters,
            page_size=self.export_max_rows,
        )

        return count, data

    def _export_csv(self, return_url: str) -> Response:
        """Export records as a streamed CSV response.

        Args:
            return_url: Redirect target when export is no longer allowed.

        Returns:
            Response: CSV response object.
        """
        count, data = self._export_data()

        class Echo:
            """Minimal file-like writer used by the CSV module."""

            def write(self, value):
                return value

        writer = csv.writer(Echo())

        def generate():
            titles = [c[1] for c in self._export_columns]
            yield writer.writerow(titles)

            for row in data:
                vals = [self.get_export_value(row, c[0]) for c in self._export_columns]
                yield writer.writerow(vals)

        filename = self.get_export_name(export_type="csv")
        disposition = "attachment;filename=%s" % (secure_filename(filename),)

        return Response(
            stream_with_context(generate()),
            headers={"Content-Disposition": disposition},
            mimetype="text/csv",
        )

    def _export_tablib(self, export_type: str, return_url: str) -> Response:
        """Export records in a variety of tabular formats.

        Args:
            export_type: Export format such as ``json``, ``yaml``, ``html``, or
                ``xlsx``.
            return_url: Redirect target if export fails.

        Returns:
            Response: Response containing the exported file.
        """
        filename = self.get_export_name(export_type)
        disposition = "attachment;filename=%s" % (secure_filename(filename),)

        mimetype, encoding = mimetypes.guess_type(filename)
        if not mimetype:
            mimetype = "application/octet-stream"
        if encoding:
            mimetype = "%s; charset=%s" % (mimetype, encoding)

        ds = tablib.Dataset(headers=[c[1] for c in self._export_columns])

        count, data = self._export_data()

        for row in data:
            vals = [self.get_export_value(row, c[0]) for c in self._export_columns]
            ds.append(vals)

        try:
            try:
                response_data = ds.export(format=export_type)
            except AttributeError:
                response_data = getattr(ds, export_type)
        except (AttributeError, tablib.UnsupportedFormat):
            flash(
                gettext('Export type "%(type)s" not supported.', type=export_type),
                "error",
            )
            return redirect(return_url)

        return Response(
            response_data,
            headers={"Content-Disposition": disposition},
            mimetype=mimetype,
        )

    @expose_url("/export/<export_type>/")
    def export(self, export_type: str) -> Response:
        """Handle export requests for a given file format.

        Args:
            export_type: Output format to generate.

        Returns:
            Response: File response or redirect.
        """
        return_url = (
            self.get_redirect_target() if hasattr(self, "get_redirect_target") else "#"
        )

        if not self.can_export or (export_type not in self.export_types):
            flash(gettext("Permission denied."), "error")
            return redirect(return_url)

        if export_type == "csv":
            return self._export_csv(return_url)
        else:
            return self._export_tablib(export_type, return_url)
