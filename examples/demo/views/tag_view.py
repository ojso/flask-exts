from flask_exts.admin.sqla import ModelView
from ..models.tag import Tag
from ..models import db

tagview = ModelView(Tag, db.session)
