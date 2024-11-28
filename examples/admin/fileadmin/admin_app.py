import os.path as op
from flask_exts.admin import Admin
from flask_exts.admin.file_admin import LocalFileAdmin

class FileAdmin(LocalFileAdmin):
    upload_modal = True
    rename_modal = True

# Create admin interface
admin = Admin(name="Example: File Admin Views")

# Create file admin view
path = op.join(op.dirname(__file__), "tmp")
file_admin_view = FileAdmin(path, name="TmpFiles")
# file_admin_view.rename_modal=True

admin.add_view(file_admin_view)
