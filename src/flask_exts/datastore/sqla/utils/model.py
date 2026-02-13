from sqlalchemy import inspect


def get_model_mapper(model):
    """
    Return the mapper for a given model
    """
    return inspect(model)


def get_primary_key(model):
    """
    Return primary key name from a model. If the primary key consists of multiple columns,
    return the corresponding tuple
    """
    mapper = inspect(model)
    pks = [col.name for col in mapper.primary_key]
    if len(pks) == 1:
        return pks[0]
    elif len(pks) > 1:
        return tuple(pks)
    else:
        return None


def has_multiple_pks(model):
    """
    Return True if the model has multiple primary keys, False otherwise
    """
    mapper = inspect(model)
    return len(mapper.primary_key) > 1


def get_model_tables(model):
    """
    Return a set of table names that the model is mapped to
    """
    mapper = inspect(model)
    return mapper.tables
