from .view import View
from .exposer import expose_url
from .action_mixin import ActionMixin
from .flask_mixin import FlaskMixin


class ActionView(View, ActionMixin, FlaskMixin):
    @expose_url("/action/", methods=("POST",))
    def action_view(self):
        """
        Mass-model action view.
        """
        return self.handle_action()
