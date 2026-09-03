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
    """
    Export operations mixin / 导出操作功能混入类

    English summary: Provides data export capabilities for CSV and other tabular file formats.
    中文说明：提供数据导出能力，支持 CSV 及其他表格格式。
    """

    can_export: bool = False
    """English: comment / 是否允许导出; export is enabled when can_export is True / 导出功能在 can_export 为 True 时启用."""

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
        """
        获取要导出的数据。

        验证导出列中的格式化器，然后获取过滤和搜索后的数据。

        Returns:
            Tuple[Optional[int], List[Any]]: (总行数, 数据列表)

        Raises:
            NotImplementedError: 如果使用了不支持的宏
        """
        # English: comment / 验证格式化器
        for col, func in (self.column_formatters_export or {}).items():
            # English: comment / 跳过未导出的列
            # skip checking columns not being exported
            if col not in [col for col, _ in self._export_columns]:
                continue

            if func.__name__ == "inner":
                raise NotImplementedError(
                    "Macros are not implemented in export. Exclude column in"
                    " column_formatters_export, column_export_list. "
                    "Column: %s" % (col,)
                )

        # English: comment / 获取列表参数
        # Grab parameters from URL
        view_args = self._get_list_args()

        # English: comment / 根据索引映射列名
        # Map column index to column name
        sort_column = self._get_column_by_idx(view_args.sort)
        if sort_column is not None:
            sort_column = sort_column[0]

        # Get count and data
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
        """
        Export a CSV of records as a stream.
        以流的形式导出 CSV 记录。

        Args:
            return_url (str): 重定向 URL

        Returns:
            Response: CSV 响应
        """
        count, data = self._export_data()

        # English: CSV Echo / CSV Echo 类用于流式写入
        class Echo:
            """English: An object that implements just the / 实现类似文件的写方法的对象An object that implements just the write method of the file-like interface."""

            def write(self, value):
                """English: Write the value by returning it / 返回值而不是存储在缓冲区Write the value by returning it, instead of storing in a buffer."""
                return value

        writer = csv.writer(Echo())

        def generate():
            # English: comment / 在开始处添加列标题
            # Append the column titles at the beginning
            titles = [c[1] for c in self._export_columns]
            yield writer.writerow(titles)

            # English: comment / 逐行生成数据
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
        """
        Exports a variety of formats using the tablib library.

        使用 tablib 库导出多种格式。

        Args:
            export_type (str): 导出格式（如 'json', 'yaml', 'html', 'xlsx' 等）
            return_url (str): 重定向 URL

        Returns:
            Response: 导出文件响应
        """
        filename = self.get_export_name(export_type)
        disposition = "attachment;filename=%s" % (secure_filename(filename),)

        # English: MIME type / 猜测 MIME 类型
        mimetype, encoding = mimetypes.guess_type(filename)
        if not mimetype:
            mimetype = "application/octet-stream"
        if encoding:
            mimetype = "%s; charset=%s" % (mimetype, encoding)

        # English: create tablib / 创建 tablib 数据集
        ds = tablib.Dataset(headers=[c[1] for c in self._export_columns])

        count, data = self._export_data()

        # English: comment / 添加数据行
        for row in data:
            vals = [self.get_export_value(row, c[0]) for c in self._export_columns]
            ds.append(vals)

        # English: comment / 导出为指定格式
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
        """
        导出处理器（路由处理）。

        根据导出类型调用相应的导出方法。

        Args:
            export_type (str): 导出格式

        Returns:
            Response: 导出文件或重定向
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
