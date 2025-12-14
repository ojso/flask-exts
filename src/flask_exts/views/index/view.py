from ...admin import View, expose_url


class IndexView(View):
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

    @expose_url("/")
    def index(self):
        return self.render("index.html")

    @expose_url("/admin/")
    def admin_index(self):
        return self.render("admin/index.html")
