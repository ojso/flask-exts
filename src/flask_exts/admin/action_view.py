from .view import View
from .decorate import expose
from .action_mixin import ActionMixin


class ActionView(View, ActionMixin):
    @expose("/action/", methods=("POST",))
    def action_view(self):
        """
        Mass-model action view.
        """
        return self.handle_action()
