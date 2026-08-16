"""
导出操作 (Export Operations)

负责导出模型数据的操作。
支持 CSV 和其他由 tablib 支持的格式。
"""

from typing import Optional, List, Tuple, Any
import csv
import mimetypes
import tablib
from flask import Response, redirect, flash, request, jsonify, abort, stream_with_context
from flask_babel import gettext
from werkzeug.utils import secure_filename


class ExportOperationsMixin:
    """
    导出操作功能混入类。

    提供数据导出功能，支持 CSV 和其他格式。
    """

    # 导出配置属性（继承自 ModelView）
    export_max_rows: int = 0
    """导出的最大行数，0 表示无限制"""

    export_types: List[str] = ["csv"]
    """可用的导出类型列表"""

    can_export: bool = False
    """是否允许导出"""

    def _export_data(self) -> Tuple[Optional[int], List[Any]]:
        """
        获取要导出的数据。

        验证导出列中的格式化器，然后获取过滤和搜索后的数据。

        Returns:
            Tuple[Optional[int], List[Any]]: (总行数, 数据列表)

        Raises:
            NotImplementedError: 如果使用了不支持的宏
        """
        # 验证格式化器
        for col, func in (self.column_formatters_export or {}).items():
            # 跳过未导出的列
            if col not in [col for col, _ in self._export_columns]:
                continue

            if func.__name__ == "inner":
                raise NotImplementedError(
                    "Macros are not implemented in export. Exclude column in"
                    " column_formatters_export, column_export_list. "
                    "Column: %s" % (col,)
                )

        # 获取列表参数
        view_args = self._get_list_args()

        # 根据索引映射列名
        sort_column = self._get_column_by_idx(view_args.sort)
        if sort_column is not None:
            sort_column = sort_column[0]

        # 获取数据
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
        以流的形式导出 CSV 记录。

        Args:
            return_url (str): 重定向 URL

        Returns:
            Response: CSV 响应
        """
        count, data = self._export_data()

        # CSV Echo 类用于流式写入
        class Echo:
            """实现类似文件的写方法的对象"""

            def write(self, value):
                """返回值而不是存储在缓冲区"""
                return value

        writer = csv.writer(Echo())

        def generate():
            # 在开始处添加列标题
            titles = [c[1] for c in self._export_columns]
            yield writer.writerow(titles)

            # 逐行生成数据
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
        使用 tablib 库导出多种格式。

        Args:
            export_type (str): 导出格式（如 'json', 'yaml', 'html', 'xlsx' 等）
            return_url (str): 重定向 URL

        Returns:
            Response: 导出文件响应
        """
        filename = self.get_export_name(export_type)
        disposition = "attachment;filename=%s" % (secure_filename(filename),)

        # 猜测 MIME 类型
        mimetype, encoding = mimetypes.guess_type(filename)
        if not mimetype:
            mimetype = "application/octet-stream"
        if encoding:
            mimetype = "%s; charset=%s" % (mimetype, encoding)

        # 创建 tablib 数据集
        ds = tablib.Dataset(headers=[c[1] for c in self._export_columns])

        count, data = self._export_data()

        # 添加数据行
        for row in data:
            vals = [self.get_export_value(row, c[0]) for c in self._export_columns]
            ds.append(vals)

        # 导出为指定格式
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

    def export(self, export_type: str) -> Response:
        """
        导出处理器（路由处理）。

        根据导出类型调用相应的导出方法。

        Args:
            export_type (str): 导出格式

        Returns:
            Response: 导出文件或重定向
        """
        return_url = self.get_redirect_target() if hasattr(self, 'get_redirect_target') else "#"

        if not self.can_export or (export_type not in self.export_types):
            flash(gettext("Permission denied."), "error")
            return redirect(return_url)

        if export_type == "csv":
            return self._export_csv(return_url)
        else:
            return self._export_tablib(export_type, return_url)
