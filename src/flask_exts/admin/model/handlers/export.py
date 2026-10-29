import csv
import mimetypes
import time
from typing import Any

import tablib
from flask import Response, flash, redirect, stream_with_context
from flask_babel import gettext
from werkzeug.utils import secure_filename


class ExportHandler:
    """Handler for exporting model data in tabular formats."""

    def __init__(self, view):
        self.view = view
        self._export_columns = view._export_columns

    def get_export_name(self, export_type: str = "csv") -> str:
        """Return the generated export filename.

        Args:
            export_type: Export format name, for example ``csv``.

        Returns:
            str: Export filename.
        """

        filename = (
            f"{self.view.name}_{time.strftime('%Y-%m-%d_%H-%M-%S')}.{export_type}"
        )

        return filename

    def _export_data(self) -> tuple[int | None, list[Any]]:
        """Return the rows to be exported.

        The method validates export formatters and then requests the filtered,
        sorted, and paginated data set needed for the export.

        Returns:
            tuple[int | None, list[Any]]: ``(count, rows)``.

        Raises:
            NotImplementedError: If unsupported macros are used in export
                formatters.
        """
        for col, func in (self.view.column_formatters_export or {}).items():
            if col not in [col for col, _ in self._export_columns]:
                continue

            if func.__name__ == "inner":
                raise NotImplementedError(
                    "Macros are not implemented in export. Exclude column in"
                    " column_formatters_export, column_export_list. "
                    f"Column: {col}"
                )

        view_args = self.view.get_list_args()
        sort_column = self.view._get_column_by_idx(view_args.sort)
        if sort_column is not None:
            sort_column = sort_column[0]

        count, data = self.view.get_list(
            search=view_args.search,
            filters=view_args.filters,
            sort_field=sort_column,
            sort_desc=view_args.sort_desc,
            page=0,
            page_size=self.view.export_max_rows,
        )

        return count, data

    def export_csv(self, return_url: str) -> Response:
        """Export records as a streamed CSV response.

        Args:
            return_url: Redirect target when export is no longer allowed.

        Returns:
            Response: CSV response object.
        """
        _count, data = self._export_data()

        class Echo:
            """Minimal file-like writer used by the CSV module."""

            def write(self, value):
                return value

        writer = csv.writer(Echo())

        def generate():
            titles = [c[1] for c in self._export_columns]
            yield writer.writerow(titles)

            for row in data:
                vals = [
                    self.view.get_export_value(row, c[0]) for c in self._export_columns
                ]
                yield writer.writerow(vals)

        filename = self.get_export_name(export_type="csv")
        disposition = f"attachment;filename={secure_filename(filename)}"

        return Response(
            stream_with_context(generate()),
            headers={"Content-Disposition": disposition},
            mimetype="text/csv",
        )

    def export_tablib(self, export_type: str, return_url: str) -> Response:
        """Export records in a variety of tabular formats.

        Args:
            export_type: Export format such as ``json``, ``yaml``, or ``xlsx``.
            return_url: Redirect target if export fails.

        Returns:
            Response: Response containing the exported file.
        """
        filename = self.get_export_name(export_type)
        disposition = f"attachment;filename={secure_filename(filename)}"

        mimetype, encoding = mimetypes.guess_type(filename)
        if not mimetype:
            mimetype = "application/octet-stream"
        if encoding:
            mimetype = f"{mimetype}; charset={encoding}"

        ds = tablib.Dataset(headers=[c[1] for c in self._export_columns])

        _count, data = self._export_data()

        for row in data:
            vals = [self.view.get_export_value(row, c[0]) for c in self._export_columns]
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
