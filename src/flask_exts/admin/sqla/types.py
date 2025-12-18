from typing import Union, Sequence
import sqlalchemy

T_COLUMN_LIST = Sequence[Union[str, "sqlalchemy.Column"]]
