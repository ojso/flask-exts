from .model import get_model_mapper


def need_join(model, table):
    mapper = get_model_mapper(model)
    return table not in mapper.tables
