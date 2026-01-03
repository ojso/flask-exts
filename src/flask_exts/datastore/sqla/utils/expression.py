from .model import get_model_mapper


def need_join(model, table):
    mapper = get_model_mapper(model)
    return table not in mapper.tables

def parse_like_term(term):
    if term.startswith("^"):
        stmt = "%s%%" % term[1:]
    elif term.startswith("="):
        stmt = term[1:]
    else:
        stmt = "%%%s%%" % term

    return stmt