from flask_exts.admin.sqla import ModelView
from ..models import db
from ..models.keyword import Keyword


class KeywordView(ModelView):
    column_list = ("id", "keyword")


keywordview = KeywordView(Keyword, db.session)
