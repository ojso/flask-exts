from ..admin import View, expose_url


class IndexView(View):
    allow_access = True

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

    @expose_url("/")
    def index(self):
        return self.render("index.html")

    @expose_url("/admin/")
    def adminindex(self):
        return self.render("admin/index.html")
