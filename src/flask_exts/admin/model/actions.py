import inspect
from wtforms.fields import HiddenField
from flask import request
from flask import redirect
from flask import flash
from flask_babel import gettext, ngettext, lazy_gettext
from ..exposer import expose_url
from ..exposer import expose_action


class ActionsMixin:
    """
    Mixin to add mass-model actions to a view. To create an action, define a method and decorate it with `@expose_action` decorator. For example:
        class MyView(View):
            @expose_action('delete', 'Delete', confirmation='Are you sure you want to delete selected items?')
            def action_delete(self, ids):
                # perform delete action on the items with the given ids
                pass
    """

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
        self._action_form_class = self.init_action_form_class()
        super().__init__(*args, **kwargs)

    def init_actions(self):
        for name, attr in inspect.getmembers(self, predicate=inspect.ismethod):
            if callable(attr) and hasattr(attr, "_action"):
                name, text, confirmation = attr._action
                self._actions[name] = attr
                self._actions_data.append((name, text, confirmation))

    def init_action_form_class(self):
        """
        Create form class for a model action.
        """

        class ActionForm(self.form_base_class):
            action = HiddenField()
            # get_redirect_target() will use url to redirect after action is performed.
            url = HiddenField()
            # rowid = HiddenField() # Not needed since we get selected ids from request.form.getlist('rowid')

        return ActionForm

    def is_action_allowed(self, name):
        """
        Override this method to allow or disallow actions based on some condition.
        The default implementation only checks if the particular action is not in `action_disallowed_list`.
        """
        return name not in self.action_disallowed_list

    def get_list_actions(self):
        """
        Return a list and a dictionary of allowed actions.
        """
        actions_data = []
        for action in self._actions_data:
            name, text, confirmation = action
            if self.is_action_allowed(name):
                actions_data.append((name, text, confirmation))
        return actions_data

    def action_form(self, *args, **kwargs):
        """
        Instantiate model action form and return it.

        Override to implement custom behavior.
        """
        return self._action_form_class(*args, **kwargs)

    def delete_models_by_pk_ids(self, ids: list):
        """
        Delete models by their IDs.

        :param ids:
            List of model IDs to delete
        """

        raise NotImplementedError()

    @expose_url("/action/", methods=("POST",))
    def action_view(self):
        """
        Mass-model action view.
        """
        form = self._action_form_class()
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

    @expose_action(
        "delete",
        lazy_gettext("Delete"),
        lazy_gettext("Are you sure you want to delete selected records?"),
    )
    def action_delete(self, ids: list):
        count = self.delete_models_by_pk_ids(ids)
        flash(
            ngettext(
                "Record was successfully deleted.",
                "%(count)s records were successfully deleted.",
                count,
                count=count,
            ),
            "success",
        )
