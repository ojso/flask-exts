from .base_admin import BaseAdmin
from ..utils.authorize import authorize_allow
class Admin(BaseAdmin):

    def allow(self, *args, **kwargs):
         return authorize_allow(*args, **kwargs)
    
    def init_views(self):
        from ..views.index_view import IndexView
        from ..views.user_view import UserView
        index_view = IndexView()
        self.add_view(index_view, is_menu=False)

        user_view = UserView()
        self.add_view(user_view, is_menu=False)