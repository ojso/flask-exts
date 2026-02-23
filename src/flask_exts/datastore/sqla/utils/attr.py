from typing import Tuple, List
from sqlalchemy import inspect
from sqlalchemy.orm import ColumnProperty
from sqlalchemy.orm import RelationshipProperty
from sqlalchemy.orm.attributes import InstrumentedAttribute
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.ext.associationproxy import AssociationProxy


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
) -> Tuple[InstrumentedAttribute, List[InstrumentedAttribute]]:
    """
    Resolve a dot-separated field path (e.g., 'profile.contact.email')
    starting from `model`, handling columns and relationships.

    Returns:
        (final_attr, join_path)
        - final_attr: The terminal InstrumentedAttribute (e.g., Contact.email)
        - join_path: List of relationship attributes for explicit joins (e.g., [User.profile, Profile.contact])
    """
    final_attr = None
    join_path: List[InstrumentedAttribute] = []

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
            remote_attr = attr.remote_attr
            final_attr = remote_attr
            break
        else:
            raise ValueError(
                f"Unsupported attribute type for '{model}':'{part}': {type(attr)}"
            )

    if final_attr is None:
        raise RuntimeError("Failed to resolve path — no terminal attribute found.")

    return final_attr, join_path
