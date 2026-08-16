"""
Concrete extension implementations for Exts v2 architecture.

Each extension is now a self-contained module that can be:
- Registered dynamically
- Tested independently
- Enabled/disabled selectively
- Reused in other projects
"""

# extensions/__init__.py

from .database_ext import DatabaseExtension
from .babel_ext import BabelExtension
from .template_ext import TemplateExtension
from .email_ext import EmailExtension
from .usercenter_ext import UserCenterExtension
from .security_ext import SecurityExtension
from .admin_ext import AdminExtension
from .startup_ext import StartupExtension

__all__ = [
    'DatabaseExtension',
    'BabelExtension',
    'TemplateExtension',
    'EmailExtension',
    'UserCenterExtension',
    'SecurityExtension',
    'AdminExtension',
    'StartupExtension',
]
