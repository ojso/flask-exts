from flask_exts.admin.sqla.view import SqlaModelView
from ..models.tag import Tag

tagview = SqlaModelView(Tag)
