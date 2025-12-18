from typing import Sequence, Dict, Callable, Any

T_COLUMN_LIST = Sequence[str]
T_FORMATTER = Callable[[Any, Any, Any], Any]
T_FORMATTERS = Dict[type, T_FORMATTER]
