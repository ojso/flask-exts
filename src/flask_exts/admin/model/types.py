from collections.abc import Callable, Sequence
from typing import Any

T_COLUMN_LIST = Sequence[str]
T_FORMATTERS = dict[type, Callable[[Any, Any, Any], Any]]
