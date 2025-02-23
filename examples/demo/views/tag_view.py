from flask_exts.admin.sqla import ModelView
from ..models.tag import Tag

tagview = ModelView(Tag)
