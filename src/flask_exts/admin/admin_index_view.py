from .wraps import expose
from .view import BaseView


class AdminIndexView(BaseView):
    """
    Default administrative interface index page when visiting the ``/admin/`` URL.
    """

    def __init__(
        self,
        name=None,
        category=None,
        endpoint=None,
        url=None,
        template_folder=None,
        static_folder=None,
        static_url_path=None,
        menu_class_name=None,
        menu_icon_type=None,
        menu_icon_value=None,
        index_template=None,
    ):
        super().__init__(
            name=name,
            category=category,
            endpoint=endpoint,
            url=url,
            template_folder=template_folder,
            static_folder=static_folder,
            static_url_path=static_url_path,
            menu_class_name=menu_class_name,
            menu_icon_type=menu_icon_type,
            menu_icon_value=menu_icon_value,
        )
        self._index_template = index_template or "admin/index.html"

    @expose()
    def index(self):
        return self.render(self._index_template)
