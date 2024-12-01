from flask_exts.admin import expose
from flask_exts.admin import BaseView


class MyView(BaseView):
    @expose("/")
    def index(self):
        return self.render("index.html")
    
myview = MyView(name="Home",url="/") 
