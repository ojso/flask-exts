import inspect
from wtforms.fields import HiddenField
from flask import request
from flask import redirect
from ..exposer import expose_url


class ActionMixin:

    action_disallowed_list = []
    """
        Set of disallowed action names. For example, if you want to disable
        mass model deletion, do something like this:

            class MyView(View):
                action_disallowed_list = ['delete']
    """

    def __init__(self, *args, **kwargs):
        self._actions = {}
        self._actions_data = []
        for name, attr in inspect.getmembers(self, predicate=inspect.ismethod):
            if callable(attr) and hasattr(attr, "_action"):
                name, text, confirmation = attr._action
                self._actions[name] = attr
                self._actions_data.append((name, text, confirmation))

        self.actions_form_class = self._get_actions_form()

        super().__init__(*args, **kwargs)

    def is_action_allowed(self, name):
        """
        Override this method to allow or disallow actions based on some condition.
        The default implementation only checks if the particular action is not in `action_disallowed_list`.
        """
        return name not in self.action_disallowed_list

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

    def _get_actions_form(self):
        """
        Create form class for a model action.
        """

        class ActionForm(self.form_base_class):
            action = HiddenField()
            url = HiddenField() # get_redirect_target() will use the url to redirect after action is performed, 
            # rowid = HiddenField() # Not needed since we get selected ids from request.form.getlist('rowid')

        return ActionForm

    @expose_url("/action/", methods=("POST",))
    def action_view(self):
        """
        Mass-model action view.
        """
        form = self.actions_form_class()
        if form.validate():
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
