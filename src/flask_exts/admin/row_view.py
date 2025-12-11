from .view import BaseView
from .decorate import expose
from .action_mixin import ActionMixin

class RowView(BaseView, ActionMixin):
    """
    Row view.
    """

    @expose("/action/", methods=("POST",))
    def action_view(self):
        """
        Mass-model action view.
        """
        return self.handle_action()

    
