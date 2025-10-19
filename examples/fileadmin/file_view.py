import os.path as op
from flask_exts.views.file.local_file_view import LocalFileView

class FileView(LocalFileView):
    upload_modal = True
    rename_modal = True

# Create file admin view
path = op.join(op.dirname(__file__), "tmp")
file_view = FileView(path, name="TmpFiles")
# file_view.rename_modal=True

