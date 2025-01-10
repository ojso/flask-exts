from .base_file_view import BaseFileView
from .local_file_storage import LocalFileStorage


class LocalFileView(BaseFileView):
    """
    Local file-management interface.

    :param base_path:
        Path to the directory which will be managed
    """

    def __init__(self, base_path, *args, **kwargs):
        storage = LocalFileStorage(base_path)
        super().__init__(*args, storage=storage, **kwargs)
