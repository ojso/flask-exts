from sqlalchemy import inspect
from sqlalchemy import select
from sqlalchemy import delete
from sqlalchemy import tuple_


def get_primary_key(model):
    """
    Return primary key name from a model. If the primary key consists of multiple columns,
    return the corresponding tuple
    """
    insp = inspect(model)
    pks = [col.name for col in insp.primary_key]
    if len(pks) == 1:
        return pks[0]
    elif len(pks) > 1:
        return tuple(pks)
    else:
        return None


def get_primary_key_values(instance):
    """
    Return primary key values from an instance.
    """
    identity = inspect(instance).identity
    if len(identity) == 1:
        return identity[0]
    else:
        return identity


def has_multiple_pks(model):
    """
    Return True if the model has multiple primary keys, False otherwise
    """
    insp = inspect(model)
    return len(insp.primary_key) > 1

def need_join(model, table):
    return table not in inspect(model).tables

def stmt_delete_model_pk_ids(model, ids: list):
    """
    Return a delete statement that deletes all rows with primary key in ids
    """
    insp = inspect(model)
    primary_key = insp.primary_key
    if len(primary_key) == 1:
        pk_col = primary_key[0]
        stmt = delete(model).where(pk_col.in_(ids))
    else:
        stmt = delete(model).where(tuple_(*primary_key).in_(ids))
    return stmt

def stmt_select_model_pk_values(model):
    insp = inspect(model)
    stmt = select(*insp.primary_key)
    return stmt

