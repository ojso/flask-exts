from flask import request, redirect
from ..utils import get_redirect_target
from ..utils import flash_errors


class ActionMixin:
    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)
        cls._actions = []
        cls._actions_data = {}

        for attr_name in dir(cls):
            attr = getattr(cls, attr_name)
            if callable(attr) and hasattr(attr, "_action"):
                name, text, desc = attr._action
                cls._actions.append((name, text))
                cls._actions_data[name] = (attr, text, desc)

    # action
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
        actions = []
        actions_confirmation = {}

        for act in self._actions:
            name, text = act

            if self.is_action_allowed(name):
                actions.append((name, text))

                confirmation = self._actions_data[name][2]
                if confirmation:
                    actions_confirmation[name] = confirmation

        return actions, actions_confirmation

    def handle_action(self, return_view=None):
        """
        Handle action request.

        :param return_view:
            Name of the view to return to after the request.
            If not provided, will return user to the return url in the form
            or the list view.
        """
        form = self.action_form()

        if self.validate_form(form):
            # using getlist instead of FieldList for backward compatibility
            ids = request.form.getlist("rowid")
            action = form.action.data
            handler = self._actions_data.get(action)

            if handler and self.is_action_allowed(action):
                response = handler[0](self, ids)

                if response is not None:
                    return response
        else:
            flash_errors(form, message="Failed to perform action. %(error)s")

        if return_view:
            url = self.get_url("." + return_view)
        else:
            url = get_redirect_target() or self.get_url(".index_view")

        return redirect(url)
