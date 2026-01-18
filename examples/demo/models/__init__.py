from flask_exts.datastore.sqla import db


def init_models():
    from . import myuser
    from . import keyword
    from . import myuser_keyword
    from . import tag
    from . import author
    from . import post
    from . import post_tag
    from . import tree
