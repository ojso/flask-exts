import os.path as op
from flask_exts.admin import Admin
from flask_exts.admin.file_admin import LocalFileAdmin

# Create admin interface
admin = Admin(name="Example: File Admin Views")

# Create file admin view
path = op.join(op.dirname(__file__), "tmp")
file_admin_view = LocalFileAdmin(path, name="TmpFiles")
# file_admin_view.rename_modal=True

admin.add_view(file_admin_view)
