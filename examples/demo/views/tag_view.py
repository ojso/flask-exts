from flask_exts.admin.sqla.view import SqlaModelView
from ..models.tag import Tag

class TagView(SqlaModelView):
    # can_view_details = True
    pass
    
tagview = TagView(Tag)
