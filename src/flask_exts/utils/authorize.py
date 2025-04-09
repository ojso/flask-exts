from flask_login import current_user
from ..proxies import current_authorizer


def authorize_allow(*args, **kwargs):
    if "user" in kwargs:
        user = kwargs["user"]
    else:
        user = current_user
        
    if current_authorizer.is_root_user(user):
        return True
    
    if "role_need" in kwargs:
        if current_authorizer.has_role(user, kwargs["role_need"]):
            return True
    elif "resource" in kwargs and "method" in kwargs:
        if current_authorizer.allow(user, kwargs["resource"], kwargs["method"]):
            return True
        
    return False
