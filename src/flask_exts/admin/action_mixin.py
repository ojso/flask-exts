import inspect
from wtforms.fields import HiddenField
from flask import request
from flask import redirect
from .exposer import expose_url


class ActionMixin:
    def __init__(self, *args, **kwargs):
        self._actions = {}
        self._actions_data = []
        for name, attr in inspect.getmembers(self, predicate=inspect.ismethod):
            if callable(attr) and hasattr(attr, "_action"):
                name, text, confirmation = attr._action
                self._actions[name] = attr
                self._actions_data.append((name, text, confirmation))

        super().__init__(*args, **kwargs)

    def is_action_allowed(self, name):
        """
        Verify if action with `name` is allowed.

        :param name:
            Action name
        """
        return True

    def get_actions_list(self):
        """
        Return a list and a dictionary of allowed actions.
        """
        actions_data = []
        for action in self._actions_data:
            name, text, confirmation = action
            if self.is_action_allowed(name):
                actions_data.append((name, text, confirmation))
        return actions_data

    @expose_url("/action/", methods=("POST",))
    def action_view(self):
        """
        Mass-model action view.
        """
        return self.handle_action()
    
    def handle_action(self):
        """
        Handle action request.
        """
        form = self.action_form()
        if form.validate_on_submit():
            # using getlist instead of FieldList for backward compatibility
            ids = request.form.getlist("rowid")
            action = form.action.data
            handler = self._actions.get(action)

            if handler and self.is_action_allowed(action):
                response = handler(ids)
                if response is not None:
                    return response
        else:
            form.flash_errors(message="Failed to perform action. %(error)s")

        return redirect(self.get_redirect_target())
