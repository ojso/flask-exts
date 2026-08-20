
from sqlalchemy import inspect
from ...datastore.sqla.utils import get_field_with_path


class FieldPlaceholder:
    """
    Field placeholder for model convertors.
    """

    def __init__(self, field):
        self.field = field


# Get list of fields and generate form
def get_model_form(
    model,
    converter,
    base_class,
    only=None,
    exclude=None,
    field_args=None,
    hidden_pk=False,
    extra_fields=None,
):
    """
    Generate form from the model.

    :param model:
        Model to generate form from
    :param converter:
        Converter class to use
    :param base_class:
        Base form class
    :param only:
        Include fields
    :param exclude:
        Exclude fields
    :param field_args:
        Dictionary with additional field arguments
    :param hidden_pk:
        Generate hidden field with model primary key or not
    """

    field_args = field_args or {}

    mapper = inspect(model)

    if only:
        properties = []
        for name in only:
            if extra_fields and name in extra_fields:
                properties.append((name, FieldPlaceholder(extra_fields[name])))
            else:
                column, _path = get_field_with_path(model, name)
                properties.append((column.key, column.property))
    else:
        properties = [(p.key, p) for p in mapper.attrs]
        if exclude:
            properties = [x for x in properties if x[0] not in exclude]

    field_dict = {}
    for name, p in properties:
        # Ignore protected properties
        if name.startswith("_"):
            continue

        field = converter.convert(
            model, mapper, name, p, field_args.get(name), hidden_pk
        )
        if field is not None:
            field_dict[name] = field

    # Contribute extra fields
    if not only and extra_fields:
        for name, field in extra_fields.items():
            unbound = field
            field_dict[name] = unbound.field_class(*unbound.args, **unbound.kwargs)

    return type(model.__name__ + "Form", (base_class,), field_dict)
