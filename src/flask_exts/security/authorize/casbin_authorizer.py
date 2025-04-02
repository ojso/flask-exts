from abc import ABC
from abc import abstractmethod
import os.path
from casbin.model import Model
from casbin import Enforcer

from .base import BaseAuthorizer
from .casbin_sqlalchemy_adapter import Adapter as SqlalchemyAdapter
from ..proxies import current_authorizer

CASBIN_RBAC_MODEL = """
[request_definition]
r = sub, obj, act

[policy_definition]
p = sub, obj, act

[role_definition]
g = _, _

[policy_effect]
e = some(where (p.eft == allow))

[matchers]
m = g(r.sub, p.sub) && r.obj == p.obj && r.act == p.act
"""


def _authorizer_context_processor():
    return dict(current_authorizer=current_authorizer)


class CasbinAuthorizer(BaseAuthorizer):
    """
    Casbin Enforce decorator
    """

    m = None
    e = None

    def __init__(self, app=None, adapter=None, watcher=None):
        """
        Args:
            app: Flask App object to get Casbin Model
            adapter: Casbin Adapter
        """
        self.app = app
        self.adapter = adapter or SqlalchemyAdapter()
        self.watcher = watcher
        self._owner_loader = None
        if self.app is not None:
            self.init_app(self.app)

    def init_app(self, app, add_context_processor=False):
        self.app = app
        m = Model()
        if app.config.get("CASBIN_MODEL", None) is not None:
            m_path = os.path.join(app.instance_path, app.config.get("CASBIN_MODEL"))
            m.load_model(m_path)
        else:
            m.load_model_from_text(CASBIN_RBAC_MODEL)
        self.m = m

        if add_context_processor:
            app.context_processor(_authorizer_context_processor)

    def allow(self, user, *source):
        e = self.get_casbin_enforcer()
        return e.enforce(user.name, *source)

    def get_casbin_enforcer(self):
        if self.e is None:
            self.e = Enforcer(self.m, self.adapter)
            if self.watcher:
                self.e.set_watcher(self.watcher)
        if self.e.watcher and self.e.watcher.should_reload():
            self.e.watcher.update_callback()
        return self.e

    def set_watcher(self, watcher):
        """
        Set the watcher to use with the underlying casbin enforcer
        Args:
            watcher (object):
        Returns:
            None
        """
        self.watcher = watcher
