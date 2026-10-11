from .admin_ext import AdminExtension
from .babel_ext import BabelExtension
from .database_ext import DatabaseExtension
from .emailer_ext import EmailerExtension
from .frontend_ext import FrontendExtension
from .login_ext import LoginExtension
from .portal_ext import PortalExtension
from .security_ext import SecurityExtension
from .usercenter_ext import UserCenterExtension
from .userstore_ext import UserStoreExtension

BUILTIN_EXTENSIONS = (
    BabelExtension,
    DatabaseExtension,
    EmailerExtension,
    FrontendExtension,
    LoginExtension,
    SecurityExtension,
    UserCenterExtension,
    UserStoreExtension,
    AdminExtension,
    PortalExtension,
)


__all__ = [
    "BUILTIN_EXTENSIONS",
]
