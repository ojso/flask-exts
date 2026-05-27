import operator
from functools import reduce
from sqlalchemy import inspect
from sqlalchemy.orm import aliased
from sqlalchemy.sql import select, delete
from sqlalchemy.sql import and_, or_, tuple_, desc, func
from sqlalchemy.orm import joinedload, selectinload
from sqlalchemy.orm.attributes import InstrumentedAttribute
from sqlalchemy.orm.util import AliasedClass
from sqlalchemy.sql.elements import ColumnElement
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


class Query:
    @staticmethod
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

    @staticmethod
    def has_multiple_pks(model):
        """
        Return True if the model has multiple primary keys, False otherwise
        """
        mapper = inspect(model)
        return len(mapper.primary_key) > 1

    @staticmethod
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

    @staticmethod
    def get_instance_identity(instance):
        """
        Return primary key values from an instance.
        """
        identity = inspect(instance).identity
        if len(identity) == 1:
            return identity[0]
        else:
            return identity

    @staticmethod
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

    @staticmethod
    def count(model):
        """
        Return a count of rows for the given model.
        """
        stmt = select(func.count()).select_from(model)
        return stmt

    @staticmethod
    def delete_by_pk_ids(model, ids: list):
        """
        Return a delete statement that deletes all rows with primary key in ids
        """
        mapper = inspect(model)
        primary_key = mapper.primary_key
        if len(primary_key) == 1:
            pk_col = primary_key[0]
            stmt = delete(model).where(pk_col.in_(ids))
        else:
            stmt = delete(model).where(tuple_(*primary_key).in_(ids))
        return stmt

    def __init__(self, root_model):
        self.root_model = root_model
        self._path_to_alias: dict[tuple[str, ...], AliasedClass] = {}
        self._alias_to_model: dict[AliasedClass, type] = {}
        self._joins = []
        self._filter_conditions = []
        self._search_conditions = []
        self._order_by = []
        self._limit = None
        self._offset = None
        self._joinedloads = []
        self._selectinloads = []
        self._is_join_many = False

    def _find_reusable_path(
        self, path: tuple[str, ...]
    ) -> tuple[str, tuple[str, ...], AliasedClass] | None:
        # 1. Exact match
        if path in self._path_to_alias:
            return ("match", path, self._path_to_alias[path])
        # 2. Find the longest prefix match
        best_match = None
        best_length = 0
        for existing_path, alias in self._path_to_alias.items():
            if (
                len(existing_path) < len(path)
                and path[: len(existing_path)] == existing_path
                and len(existing_path) > best_length
            ):
                best_match = ("prefix", existing_path, alias)
                best_length = len(existing_path)

        return best_match

    def join_path(self, path: str | tuple[str, ...], is_outer=True) -> AliasedClass:
        """
        Executes a JOIN operation, automatically reusing existing paths.

        :param path: The relationship path to join, either as a dot-separated string or a tuple of strings.
        :param is_outer: Whether to perform an OUTER JOIN (default: True). If False, performs an INNER JOIN.
        :return: The alias for the joined table.
        """

        if isinstance(path, str):
            path = tuple(path.split(".")) if "." in path else (path,)

        reusable = self._find_reusable_path(path)

        if reusable:
            _find, existing_path, existing_alias = reusable

            if _find == "match":
                return existing_alias
            else:
                # Continue joining from the end of the reused path
                current_alias = existing_alias
                current_model = self._alias_to_model[current_alias]
                remaining_parts = path[len(existing_path) :]
        else:
            # new path
            current_alias = None
            current_model = self.root_model
            remaining_parts = path

        for i, part in enumerate(remaining_parts):
            mapper = inspect(current_model)

            if part not in mapper.relationships:
                raise ValueError(
                    f"'{part}' is not a relationship attribute of {current_model.__name__}"
                )

            rel_prop = mapper.relationships[part]
            target_class = rel_prop.mapper.class_

            alias = aliased(target_class)

            # Store the join operation in the queue instead of applying it immediately
            if current_alias is None:
                self._joins.append((alias, getattr(current_model, part), is_outer))
            else:
                self._joins.append((alias, getattr(current_alias, part), is_outer))

            full_path = path[: len(path) - len(remaining_parts) + i + 1]
            self._path_to_alias[full_path] = alias
            self._alias_to_model[alias] = target_class

            current_alias = alias
            current_model = target_class

        return current_alias

    def _join_attr(self, attr_path: str):
        if "." in attr_path:
            relation_path = attr_path.rsplit(".", 1)[0]
            self.join_path(relation_path)

    def get_path_alias(self, path: str | tuple[str, ...]) -> AliasedClass | None:
        """Retrieves the alias for a given path."""
        if isinstance(path, str):
            path = tuple(path.split(".")) if "." in path else (path,)
        return self._path_to_alias.get(path, None)

    def get_column(self, column_path: str | tuple[str, ...]):
        """
        Retrieves a column reference based on the path.
        Supports formats like "field", "relation.field", or ("relation", "field").
        """
        if isinstance(column_path, str):
            column_path = (
                tuple(column_path.split(".")) if "." in column_path else (column_path,)
            )
        # If length is 1, it refers to a column on the root model
        if len(column_path) == 1:
            return getattr(self.root_model, column_path[0])
        # Otherwise, get the alias for the path excluding the last element (the column name)
        else:
            alias = self.get_path_alias(column_path[:-1])
            return getattr(alias, column_path[-1])

    def add_filter(self, column_path: str, operator, value):
        self._join_attr(column_path)
        self._filter_conditions.append((column_path, operator, value))

    def add_search_term(self, search: str, column_list: list[str]):
        terms = search.split(" ")
        for term in terms:
            if not term:
                continue
            self._search_conditions.append([])
            search_term = self._search_conditions[-1]
            for column_path in column_list:
                self._join_attr(column_path)
                search_term.append((column_path, term))

    def add_order_by(self, column_path: str | tuple[str, ...], is_desc: bool = False):
        """
        Adds an order by clause.
        :param column_path: The path to the column.
        :param is_desc: If True, sorts in descending order.
        """
        if "." in column_path:
            relation_path = column_path.rsplit(".", 1)[0]
            self.join_path(relation_path)
        column = self.get_column(column_path)
        if is_desc:
            self._order_by.append(desc(column))
        else:
            self._order_by.append(column)

    def limit(self, limit_val: int):
        """Sets the LIMIT for the query."""
        self._limit = limit_val
        return self

    def offset(self, offset_val: int):
        """Sets the OFFSET for the query."""
        self._offset = offset_val
        return self

    def add_eager_loads(self, joinedloads=None, selectinloads=None):
        if joinedloads:
            self._joinedloads.extend(joinedloads)
        if selectinloads:
            self._selectinloads.extend(selectinloads)

    def _like_pattern(self, column_attr, pattern: str) -> ColumnElement:
        if pattern.startswith("="):
            return column_attr == pattern[1:]
        elif pattern.startswith("^"):
            return column_attr.ilike(f"{pattern[1:]}%")
        elif pattern.endswith("$"):
            return column_attr.ilike(f"%{pattern[:-1]}")
        else:
            return column_attr.like(f"%{pattern}%")

    def _apply(self, stmt):
        # 1. Apply JOIN operations
        for alias, attr, is_outer in self._joins:
            if is_outer:
                stmt = stmt.outerjoin(alias, attr)
            else:
                stmt = stmt.join(alias, attr)

        # 2. Apply search conditions
        if self._search_conditions:
            search_clauses = []
            for search_term in self._search_conditions:
                term_clauses = []
                for column_path, term in search_term:
                    term_clauses.append(
                        self._like_pattern(self.get_column(column_path), term)
                    )
                search_clauses.append(or_(*term_clauses))
            stmt = stmt.where(and_(*search_clauses))

        # 3. Apply WHERE conditions
        if self._filter_conditions:
            conditions = []
            # Map string operators to their corresponding Python/SQLAlchemy functions
            op_map = {
                "==": operator.eq,
                "!=": operator.ne,
                ">": operator.gt,
                "<": operator.lt,
                ">=": operator.ge,
                "<=": operator.le,
            }

            for column_path, op_str, value in self._filter_conditions:
                column = self.get_column(column_path)
                match op_str:
                    case "like":
                        if "%" in value:
                            pattern = value
                        elif value.startswith("^"):
                            pattern = f"{value[1:]}%"
                        else:
                            pattern = f"%{value}%"
                        conditions.append(column.like(pattern))
                    case "not_like":
                        if "%" in value:
                            pattern = value
                        elif value.startswith("^"):
                            pattern = f"{value[1:]}%"
                        else:
                            pattern = f"%{value}%"
                        conditions.append(~column.like(pattern))
                    case "ilike":
                        if "%" in value:
                            pattern = value
                        elif value.startswith("^"):
                            pattern = f"{value[1:]}%"
                        else:
                            pattern = f"%{value}%"
                        conditions.append(column.ilike(pattern))
                    case "not_ilike":
                        #  case insensitive LIKE
                        if "%" in value:
                            pattern = value
                        elif value.startswith("^"):
                            pattern = f"{value[1:]}%"
                        else:
                            pattern = f"%{value}%"
                        conditions.append(~column.ilike(pattern))
                    case "is_null":
                        conditions.append(column.is_(None))
                    case "isnot_null":
                        conditions.append(column.isnot(None))
                    case "in":
                        conditions.append(column.in_(value))
                    case "not_in":
                        conditions.append(~column.in_(value))
                    case "between":
                        start, end = value
                        conditions.append(column.between(start, end))
                    case "not_between":
                        start, end = value
                        conditions.append(~column.between(start, end))
                    case _:
                        op_func = op_map.get(op_str)
                        conditions.append(op_func(column, value))

            # Combine all conditions with AND and apply them to the statement
            stmt = stmt.where(and_(*conditions))

        return stmt

    def build(self):
        """
        Compiles and returns the final SELECT statement.

        Applies all pending JOIN operations and dynamically added WHERE conditions
        to the base statement. Clears the internal queues to ensure idempotency.

        Returns:
            The compiled SQLAlchemy Select object.
        """
        stmt = select(self.root_model)
        stmt = self._apply(stmt)

        # Apply Eager Loading Options
        if self._joinedloads:
            stmt = stmt.options(*[joinedload(j) for j in self._joinedloads])

        if self._selectinloads:
            stmt = stmt.options(*[selectinload(j) for j in self._selectinloads])

        # Apply ORDER BY
        if self._order_by:
            stmt = stmt.order_by(*self._order_by)

        # Apply LIMIT and OFFSET
        if self._offset is not None:
            stmt = stmt.offset(self._offset)

        if self._limit is not None:
            stmt = stmt.limit(self._limit)

        return stmt

    def build_count(self):
        stmt = select(func.count()).select_from(self.root_model)
        stmt = self._apply(stmt)
        return stmt
