from flask_exts.web.sqla.view import SqlaModelView
from ..models.tag import Tag

class TagView(SqlaModelView):
    pass
    
tagview = TagView(Tag)
