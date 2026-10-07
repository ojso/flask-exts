from functools import reduce

from sqlalchemy import inspect
from sqlalchemy.ext.associationproxy import AssociationProxy
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.orm import ColumnProperty, RelationshipProperty
from sqlalchemy.orm.attributes import InstrumentedAttribute


def get_model_mapper(model):
    """
    Return the mapper for a given model
    """
    return inspect(model)


def get_model_primary_key(model):
    """
    Return primary key name from a model. If the primary key consists of multiple columns,
    return the corresponding tuple
    """
    mapper = inspect(model)
    pks = [col.name for col in mapper.primary_key]
    if len(pks) == 1:
        return pks[0]
    else:
        return tuple(pks)


def is_model_multiple_pks(model):
    """
    Return True if the model has multiple primary keys, False otherwise
    """
    mapper = inspect(model)
    return len(mapper.primary_key) > 1


def get_model_column_type(model, column_path: str):
    if "." in column_path:
        parts = column_path.split(".")
        last_model = reduce(
            lambda a, b: getattr(a, b).property.mapper.class_, parts[:-1], model
        )
        last_key = parts[-1]
    else:
        last_model = model
        last_key = column_path

    inspector = inspect(last_model)
    column = inspector.columns.get(last_key, None)
    return column.type if column is not None else None


def get_instance_identity(instance):
    """
    Return primary key values from an instance.
    """
    identity = inspect(instance).identity
    if len(identity) == 1:
        return identity[0]
    else:
        return identity


def is_instrumented_attribute(attr):
    return isinstance(attr, InstrumentedAttribute)


def is_column(attr):
    return hasattr(attr, "property") and isinstance(attr.property, ColumnProperty)


def is_relationship(attr):
    return hasattr(attr, "property") and isinstance(attr.property, RelationshipProperty)


def is_hybrid_property(model, attr_name):
    mapper = inspect(model)
    descriptor = mapper.all_orm_descriptors.get(attr_name)
    return isinstance(descriptor, hybrid_property)


def is_association_proxy(model, attr_name):
    mapper = inspect(model)
    descriptor = mapper.all_orm_descriptors.get(attr_name)
    return isinstance(descriptor, AssociationProxy)


def get_field_with_path(
    model, name: str
) -> tuple[InstrumentedAttribute, list[InstrumentedAttribute]]:
    """
    Resolve a dot-separated field path (e.g., 'profile.contact.email')
    starting from `model`, handling columns and relationships.

    Returns:
        (final_attr, join_path)
        - final_attr: The terminal InstrumentedAttribute (e.g., Contact.email)
        - join_path: List of relationship attributes for explicit joins (e.g., [User.profile, Profile.contact])
    """
    final_attr = None
    join_path: list[InstrumentedAttribute] = []

    parts = name.split(".")
    current_model = model
    for i, part in enumerate(parts):
        attr = getattr(current_model, part)
        # Case 1: Column (must be last)
        if is_column(attr):
            if i != len(parts) - 1:
                raise ValueError(
                    f"Column '{part}' cannot be followed by further path segments."
                )
            final_attr = attr
            break
        # Case 2: Relationship
        elif is_relationship(attr):
            join_path.append(attr)
            current_model = attr.property.mapper.class_
            if i == len(parts) - 1:
                final_attr = attr
                break
        # Case 3: AssociationProxy
        elif is_association_proxy(current_model, part):
            if i != len(parts) - 1:
                raise ValueError(
                    f"AssociationProxy '{part}' cannot be followed by further path segments."
                )
            # Step into the underlying relationship
            local_rel = attr.local_attr
            join_path.append(local_rel)
            final_attr = attr.remote_attr
            break
        else:
            raise ValueError(
                f"Unsupported attribute type for '{model}':'{part}': {type(attr)}"
            )

    if final_attr is None:
        raise RuntimeError("Failed to resolve path — no terminal attribute found.")

    return final_attr, join_path
