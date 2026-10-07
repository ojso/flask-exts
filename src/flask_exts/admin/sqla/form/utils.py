from sqlalchemy import inspect

from ....datastore.sqla.utils import get_field_with_path


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

    Args:
        model:
            Model to generate form from
        converter:
            Converter class to use
        base_class:
            Base form class
        only:
            Include fields
        exclude:
            Exclude fields
        field_args:
            Dictionary with additional field arguments
        hidden_pk:
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
        if hidden_pk:
            included_names = {name for name, _ in properties}
            for column in mapper.primary_key:
                prop = mapper.get_property_by_column(column)
                if prop.key not in included_names:
                    properties.append((prop.key, prop))
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
