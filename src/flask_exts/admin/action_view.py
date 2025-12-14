from .view import View
from .exposer import expose_url
from .action_mixin import ActionMixin


class ActionView(View, ActionMixin):
    @expose_url("/action/", methods=("POST",))
    def action_view(self):
        """
        Mass-model action view.
        """
        return self.handle_action()
