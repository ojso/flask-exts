import inspect
from flask import request
from flask import redirect


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

    def handle_action(self, return_view=None):
        """
        Handle action request.

        :param return_view:
            Name of the view to return to after the request.
            If not provided, will return user to the return url in the form
            or the list view.
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

        if return_view:
            url = self.get_url("." + return_view)
        else:
            url = self.get_redirect_target()

        return redirect(url)

    def get_redirect_target(self, param_name="url", endpoint=".index_view"):
        return request.values.get(param_name) or self.get_url(endpoint)
