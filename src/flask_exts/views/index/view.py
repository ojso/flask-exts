from ...admin import BaseView, expose


class IndexView(BaseView):
    def __init__(
        self,
        name="Index",
        endpoint="index",
        url="/",
    ):
        super().__init__(
            name=name,
            endpoint=endpoint,
            url=url,
        )

    def allow(self, *args, **kwargs):
        return True

    @expose("/")
    def index(self):
        return self.render("index.html")

    @expose("/admin/")
    def admin_index(self):
        return self.render("admin/index.html")
