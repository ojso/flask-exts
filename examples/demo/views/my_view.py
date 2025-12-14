from flask_exts.admin import expose_url
from flask_exts.admin import View


class MyView(View):
    @expose_url("/")
    def index(self):
        return self.render("my/index.html",x=[1,2,3])
    
myview = MyView(name="MyView") 
