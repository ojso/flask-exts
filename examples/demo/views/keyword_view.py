from flask_exts.admin.sqla.view import SqlaModelView
from ..models.keyword import Keyword


class KeywordView(SqlaModelView):
    column_list = ("id", "keyword")


keywordview = KeywordView(Keyword)
