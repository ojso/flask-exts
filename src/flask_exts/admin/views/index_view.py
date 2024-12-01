from ..wraps import expose
from ..view import BaseView


class IndexView(BaseView):
    """
    Default administrative interface index page when visiting the ``/admin/`` URL.
    """

    index_template = "admin/index.html"
    admin_index_template = "admin/admin.html"

    def __init__(
        self,
        name="Index",
        category=None,
        endpoint="index",
        url="/",
        template_folder=None,
        static_folder=None,
        static_url_path=None,
        menu_class_name=None,
        menu_icon_type=None,
        menu_icon_value=None,
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

    @expose("/")
    def index(self):
        return self.render(self.index_template)
    
    @expose("/admin/")
    def admin_index(self):
        return self.render(self.admin_index_template)
