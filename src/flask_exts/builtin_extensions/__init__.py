from .babel_ext import BabelExtension
from .database_ext import DatabaseExtension
from .email_ext import EmailExtension
from .html_ext import HtmlExtension
from .login_ext import LoginExtension
from .security_ext import SecurityExtension
from .startup_ext import StartupExtension
from .usercenter_ext import UserCenterExtension
from .userstore_ext import UserStoreExtension
from .web_ext import WebExtension

BUILTIN_EXTENSIONS = (
    BabelExtension,
    DatabaseExtension,
    EmailExtension,
    HtmlExtension,
    LoginExtension,
    SecurityExtension,
    StartupExtension,
    UserCenterExtension,
    UserStoreExtension,
    WebExtension,
)

__all__ = [
    "BUILTIN_EXTENSIONS",
]
