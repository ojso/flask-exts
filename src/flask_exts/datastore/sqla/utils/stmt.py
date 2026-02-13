from sqlalchemy import inspect
from sqlalchemy import select
from sqlalchemy import delete
from sqlalchemy import tuple_


def select_pk_values(model):
    """
    Return a select statement that selects all primary key values from a model
    """
    mapper = inspect(model)
    stmt = select(*mapper.primary_key)
    return stmt


def clear(model):
    """
    Return a delete statement that deletes all rows of the model
    """
    stmt = delete(model)
    return stmt


def delete_by_pk_ids(model, ids: list):
    """
    Return a delete statement that deletes all rows with primary key in ids
    """
    mapper = inspect(model)
    primary_key = mapper.primary_key
    if len(primary_key) == 1:
        pk_col = primary_key[0]
        stmt = delete(model).where(pk_col.in_(ids))
    else:
        stmt = delete(model).where(tuple_(*primary_key).in_(ids))
    return stmt
