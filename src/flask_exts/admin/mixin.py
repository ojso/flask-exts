"""Admin's contribution-point mixin for other extensions.

This is the admin-specific half of the generic two-phase extension lifecycle
(see ``extension_core.base.Extension``). Core stays unaware admin exists;
any extension that wants its views picked up declares that by inheriting
``AdminViewMixin`` instead of admin needing to know their names.
"""

from .view import View


class AdminViewMixin:
    """
    Mix this into an ``Extension`` to publish views to the admin instance.

    Usage::

        class PortalExtension(AdminViewMixin, Extension):
            @property
            def name(self) -> str:
                return "portal"

            def init_app(self, app):
                pass

            def get_admin_views(self):
                return [(IndexView(), False)]

    ``AdminExtension`` discovers implementers via ``isinstance`` during its
    own ``post_init`` -- after every extension's ``init_app`` has run -- so
    registration order between a provider and ``admin`` does not matter.
    """

    def get_admin_views(self) -> list[tuple[View, bool]]:
        """
        Views this extension wants registered on the admin instance.

        Returns:
            list[tuple[View, bool]]: ``(view_instance, is_menu)`` pairs
        """
        return []
