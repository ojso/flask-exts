import types
from sqlalchemy import tuple_, or_, and_, inspect
from sqlalchemy.sql.operators import eq

def filter_foreign_columns(base_table, columns):
    """
    Return list of columns that belong to passed table.

    :param base_table: Table to check against
    :param columns: List of columns to filter
    """
    return [c for c in columns if c.table == base_table]


def tuple_operator_in(model_pk, ids):
    """The tuple_ Operator only works on certain engines like MySQL or Postgresql. It does not work with sqlite.

    The function returns an or_ - operator, that containes and_ - operators for every single tuple in ids.

    Example::

      model_pk =  [ColumnA, ColumnB]
      ids = ((1,2), (1,3))

      tuple_operator(model_pk, ids) -> or_( and_( ColumnA == 1, ColumnB == 2), and_( ColumnA == 1, ColumnB == 3) )

    The returning operator can be used within a filter(), as it is just an or_ operator
    """
    ands = []
    for id in ids:
        k = []
        for i in range(len(model_pk)):
            k.append(eq(model_pk[i], id[i]))
        ands.append(and_(*k))
    if len(ands) >= 1:
        return or_(*ands)
    else:
        return None


def get_columns_for_field(field):
    if (
        not field
        or not hasattr(field, "property")
        or not hasattr(field.property, "columns")
        or not field.property.columns
    ):
        raise Exception("Invalid field %s: does not contains any columns." % field)

    return field.property.columns








