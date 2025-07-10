from flask_login import current_user
from ..proxies import _authorizer


def authorize_allow(*args, **kwargs):
    if "user" in kwargs:
        user = kwargs["user"]
    else:
        user = current_user
        
    if _authorizer.is_root_user(user):
        return True
    
    if "role_need" in kwargs:
        if _authorizer.has_role(user, kwargs["role_need"]):
            return True
    elif "resource" in kwargs and "method" in kwargs:
        if _authorizer.allow(user, kwargs["resource"], kwargs["method"]):
            return True
        
    return False
