from flask_exts.admin import expose
from flask_exts.admin import View


class MyView(View):
    @expose("/")
    def index(self):
        return self.render("my/index.html",x=[1,2,3])
    
myview = MyView(name="MyView") 
