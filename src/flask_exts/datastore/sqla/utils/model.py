from typing import Tuple, List
from sqlalchemy import inspect
from sqlalchemy.orm import ColumnProperty
from sqlalchemy.orm import RelationshipProperty
from sqlalchemy.orm.attributes import InstrumentedAttribute
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.ext.associationproxy import AssociationProxy


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
    mapper = get_model_mapper(model)
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
    mapper = get_model_mapper(model)
    return len(mapper.primary_key) > 1

def is_instrumented_attribute(attr):
    return isinstance(attr,InstrumentedAttribute)

def is_column(attr):
    return hasattr(attr, "property") and isinstance(attr.property, ColumnProperty)

def is_relationship(attr):
    return hasattr(attr, "property") and isinstance(attr.property, RelationshipProperty)

def is_hybrid(attr):
    return isinstance(attr, hybrid_property)

def is_hybrid_property(model, attr_name):
    attr = getattr(model, attr_name, None)
    return isinstance(attr, hybrid_property)


def is_association_proxy(attr):
    return isinstance(attr, AssociationProxy)


def get_field_with_path(
    model, path: str
) -> Tuple[InstrumentedAttribute, List[InstrumentedAttribute]]:
    """
    Resolve a dot-separated field path (e.g., 'profile.contact.email')
    starting from `model`, handling AssociationProxy and relationships.

    Returns:
        (final_attr, join_path)
        - final_attr: The terminal InstrumentedAttribute (e.g., Contact.email)
        - join_path: List of relationship attributes for explicit joins
                     (e.g., [User.profile, Profile.contact])
    """
    parts = path.split(".")
    current_model = model
    current_attr = None
    join_path: List[InstrumentedAttribute] = []

    for i, part in enumerate(parts):
        attr = getattr(current_model, part)
        # Case 1: Column (must be last)
        if hasattr(attr, "property") and isinstance(attr.property, ColumnProperty):
            if i != len(parts) - 1:
                raise ValueError(
                    f"Column '{part}' cannot be followed by further path segments."
                )
            current_attr = attr
            break
        # Case 2: Relationship
        elif is_relationship(attr):
            if i == len(parts) - 1:
                raise ValueError(
                    f"Cannot sort/filter on relationship '{path}' directly. "
                    "Specify a column (e.g., '{path}.id')."
                )
            join_path.append(attr)
            current_model = attr.property.mapper.class_
        # Case 3: AssociationProxy
        elif isinstance(attr, AssociationProxy):
            # Step into the underlying relationship
            local_rel_name = attr.local_attr  # str, e.g., 'profile'
            local_rel = getattr(current_model, local_rel_name)

            if not is_relationship(local_rel):
                raise ValueError(
                    f"AssociationProxy '{part}' is not backed by a relationship "
                    f"(got {type(local_rel.property).__name__})."
                )

            join_path.append(local_rel)
            target_model = local_rel.property.mapper.class_

            # Get the remote attribute (should be InstrumentedAttribute in SA 2.0)
            remote_attr = attr.remote_attr

            # If there are more parts after this proxy, recurse
            if i < len(parts) - 1:
                remaining = ".".join(parts[i + 1 :])
                final_attr, extra_joins = get_field_with_path(target_model, remaining)
                join_path.extend(extra_joins)
                return final_attr, join_path

            # This is the last part — ensure remote_attr is usable
            if isinstance(remote_attr, str):
                # Fallback for older versions (not needed in SA 2.0+, but safe)
                remote_attr = getattr(target_model, remote_attr)

            if not hasattr(remote_attr, "property"):
                raise ValueError(
                    f"Remote attribute {remote_attr} is not a mapped ORM attribute."
                )

            current_attr = remote_attr
            break
        else:
            raise ValueError(f"Unsupported attribute type for '{part}': {type(attr)}")

    if current_attr is None:
        raise RuntimeError("Failed to resolve path — no terminal attribute found.")

    return current_attr, join_path
