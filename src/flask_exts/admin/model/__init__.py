"""Admin model view package.
This package provides the model-management layer used by the admin views,
"""

from .backend import DataBackend
from .view import ModelView

__all__ = [
    "DataBackend",
    "ModelView",
]
