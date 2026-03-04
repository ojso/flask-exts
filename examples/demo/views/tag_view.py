from flask_exts.admin.sqla.view import SqlaModelView
from ..models.tag import Tag

class TagView(SqlaModelView):
    pass
    
tagview = TagView(Tag)
