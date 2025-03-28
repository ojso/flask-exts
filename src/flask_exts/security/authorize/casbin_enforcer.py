from functools import wraps
from abc import ABC
from abc import abstractmethod
from flask import request, jsonify
from ..utils import authorization_decoder
from ..utils import UnSupportedAuthType

import os.path
from casbin.model import Model
from casbin import Enforcer
from .sqlalchemy_adapter import Adapter

CASBIN_RBAC_MODEL="""
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


class CasbinEnforcer:
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
        self.adapter = adapter or Adapter()
        self.watcher = watcher
        self._owner_loader = None
        if self.app is not None:
            self.init_app(self.app)

    def init_app(self, app):
        self.app = app
        m = Model()
        if app.config.get("CASBIN_MODEL",None) is not None:
            m_path = os.path.join(app.instance_path, app.config.get("CASBIN_MODEL"))
            m.load_model(m_path)
        else:
            m.load_model_from_text(CASBIN_RBAC_MODEL)
        self.m = m
        self.user_name_headers = app.config.get("CASBIN_USER_NAME_HEADERS", "Authorization")

    def get_enforcer(self):
        if self.e is None:
            self.e = Enforcer(self.m, self.adapter)
            if self.watcher:
                self.e.set_watcher(self.watcher)
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

    def owner_loader(self, callback):
        """
        This sets the callback for get owner. The function return a owner object, or ``None``

        :param callback: The callback for retrieving a owner object.
        :type callback: callable
        """
        self._owner_loader = callback
        return callback

    def enforcer(self, func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            if self.e is None:
                self.get_enforcer()
            if self.e.watcher and self.e.watcher.should_reload():
                self.e.watcher.update_callback()
            # Set resource URI from request
            uri = str(request.path)
            # Get owner from owner_loader
            if self._owner_loader:
                for owner in self._owner_loader():
                    owner = owner.strip('"') if isinstance(owner, str) else owner
                    if self.e.enforce(owner, uri, request.method):
                        return func(*args, **kwargs)
            return (jsonify({"message": "Unauthorized"}), 401)

        return wrapper

    def enforcer_header(self, func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            if self.e is None:
                self.get_enforcer()
            if self.e.watcher and self.e.watcher.should_reload():
                self.e.watcher.update_callback()

            # Set resource URI from request
            uri = str(request.path)
            header = str.lower(self.user_name_headers)
            if header in request.headers:
                try:
                    owner = authorization_decoder(request.headers.get(header))
                    if self.e.enforce(owner, uri, request.method):
                        return func(*args, **kwargs)
                except UnSupportedAuthType:
                    return (jsonify({"message": "UnSupportedAuthType"}), 401)
                except Exception as e:
                    return (jsonify({"message": str(e)}), 401)
            return (jsonify({"message": "Unauthorized"}), 401)

        return wrapper


class Watcher(ABC):
    """
    Watcher interface as it should be implemented for flask-casbin
    """

    @abstractmethod
    def update(self):
        """
        Watcher interface as it should be implemented for flask-casbin
        Returns:
            None
        """
        pass

    @abstractmethod
    def set_update_callback(self):
        """
        Set the update callback to be used when an update is detected
        Returns:
            None
        """
        pass

    @abstractmethod
    def should_reload(self):
        """
        Method which checks if there is an update necessary for the casbin
        roles. This is called with each flask request.
        Returns:
            Bool
        """
        pass
