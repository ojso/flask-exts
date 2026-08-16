"""
排序处理器

处理查询结果的排序逻辑。
"""


class SortingHandler:
    """处理排序逻辑"""

    def __init__(self, view):
        self.view = view

    def apply_sorting(self, query, sort_column, sort_desc):
        """应用排序"""
        if sort_column:
            if sort_column in self.view.column_sortable_list:
                column = self.view.model_admin.get_column_for_field_name(
                    self.view.model, sort_column
                )
                if column is not None:
                    if sort_desc:
                        query = query.order_by(column.desc())
                    else:
                        query = query.order_by(column)

        return query
