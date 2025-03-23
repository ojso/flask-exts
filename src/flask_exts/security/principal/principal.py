from collections import deque
from typing import Callable, Deque, Optional
from flask import g, session, current_app, request
from blinker.base import Namespace
from flask import Flask

from .identity import Identity
from .identity import AnonymousIdentity


signals = Namespace()


identity_changed = signals.signal(
    "identity-changed",
    doc="""
Signal sent when the identity for a request has been changed.

Actual name: ``identity-changed``

Authentication providers should send this signal when authentication has been
successfully performed. Flask-Principal connects to this signal and
causes the identity to be saved in the session.

For example::

    from flask_principal import Identity, identity_changed

    def login_view(req):
        username = req.form.get('username')
        # check the credentials
        identity_changed.send(app, identity=Identity(username))
""",
)


identity_loaded = signals.signal(
    "identity-loaded",
    doc="""
Signal sent when the identity has been initialised for a request.

Actual name: ``identity-loaded``

Identity information providers should connect to this signal to perform two
major activities:

    1. Populate the identity object with the necessary authorization provisions.
    2. Load any additional user information.

For example::

    from flask_principal import identity_loaded, RoleNeed, UserNeed

    @identity_loaded.connect
    def on_identity_loaded(sender, identity):
        # Get the user information from the db
        user = db.get(identity.name)
        # Update the roles that a user can provide
        for role in user.roles:
            identity.provides.add(RoleNeed(role.name))
        # Save the user somewhere so we only look it up once
        identity.user = user
""",
)


def session_identity_loader() -> Optional[Identity]:
    if "identity.id" in session and "identity.auth_type" in session:
        identity = Identity(session["identity.id"], session["identity.auth_type"])
        return identity
    return None


def session_identity_saver(identity: Identity) -> None:
    session["identity.id"] = identity.id
    session["identity.auth_type"] = identity.auth_type
    session.modified = True


class Principal:
    """Principal extension

    :param app: The flask application to extend
    :param use_sessions: Whether to use sessions to extract and store
                         identification.
    :param skip_static: Whether to ignore static endpoints.
    """

    def __init__(
        self,
        app: Optional[Flask] = None,
        use_sessions: bool = True,
        skip_static: bool = False,
    ) -> None:
        self.identity_loaders: Deque[Callable[[], Optional[Identity]]] = deque()
        self.identity_savers: Deque[Callable[[Identity], None]] = deque()
        # XXX This will probably vanish for a better API
        self.use_sessions = use_sessions
        self.skip_static = skip_static

        if app is not None:
            self.init_app(app)

    def init_app(self, app: Flask) -> None:
        if hasattr(app, "static_url_path"):
            self._static_path = app.static_url_path
        else:
            self._static_path = app.static_path  # type: ignore

        app.before_request(self._on_before_request)
        identity_changed.connect(self._on_identity_changed, app)

        if self.use_sessions:
            self.identity_loader(session_identity_loader)
            self.identity_saver(session_identity_saver)

    def set_identity(self, identity: Identity) -> None:
        """Set the current identity.

        :param identity: The identity to set
        """

        self._set_thread_identity(identity)
        for saver in self.identity_savers:
            saver(identity)

    def identity_loader(
        self, f: Callable[[], Optional[Identity]]
    ) -> Callable[[], Optional[Identity]]:
        """Decorator to define a function as an identity loader.

        An identity loader function is called before request to find any
        provided identities. The first found identity is used to load from.

        For example::

            app = Flask(__name__)

            principals = Principal(app)

            @principals.identity_loader
            def load_identity_from_weird_usecase():
                return Identity('ali')
        """
        self.identity_loaders.appendleft(f)
        return f

    def identity_saver(
        self, f: Callable[[Identity], None]
    ) -> Callable[[Identity], None]:
        """Decorator to define a function as an identity saver.

        An identity loader saver is called when the identity is set to persist
        it for the next request.

        For example::

            app = Flask(__name__)

            principals = Principal(app)

            @principals.identity_saver
            def save_identity_to_weird_usecase(identity):
                my_special_cookie['identity'] = identity
        """
        self.identity_savers.appendleft(f)
        return f

    def _set_thread_identity(self, identity: Identity) -> None:
        g.identity = identity
        identity_loaded.send(
            current_app._get_current_object(), identity=identity  # type: ignore
        )

    def _on_identity_changed(self, app: Flask, identity: Identity) -> None:
        if self._is_static_route():
            return

        self.set_identity(identity)

    def _on_before_request(self) -> None:
        if self._is_static_route():
            return

        g.identity = AnonymousIdentity()
        for loader in self.identity_loaders:
            identity = loader()
            if identity is not None:
                self.set_identity(identity)
                return

    def _is_static_route(self) -> bool:
        return bool(
            self.skip_static
            and self._static_path
            and request.path.startswith(self._static_path)
        )
