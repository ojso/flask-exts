from sqlalchemy import select
from sqlalchemy import delete
from sqlalchemy import tuple_
from .model import get_model_mapper


def stmt_delete_model_pk_ids(model, ids: list):
    """
    Return a delete statement that deletes all rows with primary key in ids
    """
    mapper = get_model_mapper(model)
    primary_key = mapper.primary_key
    if len(primary_key) == 1:
        pk_col = primary_key[0]
        stmt = delete(model).where(pk_col.in_(ids))
    else:
        stmt = delete(model).where(tuple_(*primary_key).in_(ids))
    return stmt

def stmt_select_model_pk_values(model):
    """
    Return a select statement that selects all primary key values from a model
    """
    mapper = get_model_mapper(model)
    stmt = select(*mapper.primary_key)
    return stmt