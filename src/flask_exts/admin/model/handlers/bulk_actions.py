import inspect

from wtforms.fields import HiddenField


class BulkActionHandler:
    """Handler to add bulk actions to a view.

    To create an action, define a method and decorate it with `@expose_action`
    decorator.

    For example::

        class MyView(View):
            @expose_action('delete', 'Delete', confirmation='Are you sure you
            want to delete selected items?')
            def action_delete(self, ids):
                # perform delete action on the items with the given ids pass
    """

    def __init__(self, view):
        self.view = view
        self._actions = {}
        self._actions_data = []

        for name, attr in inspect.getmembers(view, predicate=inspect.ismethod):
            if callable(attr) and hasattr(attr, "_action"):
                name, text, confirmation = attr._action
                self._actions[name] = attr
                self._actions_data.append((name, text, confirmation))

    def get_bulk_action(self, name):
        return self._actions.get(name)

    def get_bulk_actions(self):
        """Return a list of allowed bulk actions."""
        actions_data = []
        for action in self._actions_data:
            name, text, confirmation = action
            if self.view.is_action_allowed(name):
                actions_data.append((name, text, confirmation))
        return actions_data

    def action_form(self, *args, **kwargs):
        """Instantiate model action form and return it."""

        class ActionForm(self.view.base_form_class):
            action = HiddenField()
            url = HiddenField()
            # rowid = HiddenField() # Not needed since we get selected ids from
            # request.form.getlist('rowid')

        return ActionForm(*args, **kwargs)
