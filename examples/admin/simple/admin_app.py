from flask_exts.admin import expose
from flask_exts.admin import BaseView
from flask_exts.admin import Admin


class MyAdminView(BaseView):
    @expose("/")
    def index(self):
        return self.render("myadmin.html")


class AnotherAdminView(BaseView):
    @expose("/")
    def index(self):
        return self.render("anotheradmin.html")

    @expose("/test/")
    def test(self):
        return self.render("test.html")


# Create admin interface
admin = Admin(name="Example: Simple Views")
admin.add_view(MyAdminView(name="view1", category="Views"))
admin.add_view(AnotherAdminView(name="view2", category="Views"))
