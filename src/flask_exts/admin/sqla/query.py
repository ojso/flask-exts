from typing import Any
from sqlalchemy import inspect
from sqlalchemy.orm import aliased
from sqlalchemy.sql import select, and_, or_, desc, func
from sqlalchemy.orm import joinedload, selectinload
import operator

AliasedClass = Any


class Query:
    def __init__(self, root_model):
        self.root_model = root_model
        self._path_to_alias: dict[tuple[str, ...], AliasedClass] = {}
        self._alias_to_model: dict[AliasedClass, type] = {}
        self._joins = []
        self._conditions = []
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

    def add_filter(self, column_path: str, value, operator):
        if "." in column_path:
            relation_path = column_path.rsplit(".", 1)[0]
            self.join_path(relation_path)
        self.add_condition(column_path, value, operator)

    def add_search(self, search):
        pass

    def add_condition(self, column_path, value, operator):
        """Dynamically adds a filter condition to the query.

        :param column_path: The path to the column (e.g., "name" or "first_b.type").
        :param value: The value to filter by.
        :param operator: The comparison operator as a string.
                         Supports "==", "!=", ">", "<", ">=", "<=", "like", "in", etc.
        """
        self._conditions.append((column_path, value, operator))

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

    def _apply(self, stmt):
        # 1. Apply JOIN operations
        for alias, attr, is_outer in self._joins:
            if is_outer:
                stmt = stmt.outerjoin(alias, attr)
            else:
                stmt = stmt.join(alias, attr)

        # 2. Apply WHERE conditions
        if self._conditions:
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

            for column_path, value, op_str in self._conditions:
                column = self.get_column(column_path)

                # Handle special operators like 'like' and 'in'
                if op_str == "like":
                    if "%" in value:
                        pattern = value
                    elif value.startswith("^"):
                        pattern = f"{value[1:]}%"
                    else:
                        pattern = f"%{value}%"
                    conditions.append(column.like(pattern))
                elif op_str == "ilike":
                    #  case insensitive LIKE
                    if "%" in value:
                        pattern = value
                    elif value.startswith("^"):
                        pattern = f"{value[1:]}%"
                    else:
                        pattern = f"%{value}%"
                    conditions.append(column.ilike(pattern))
                elif op_str == "in":
                    conditions.append(column.in_(value))
                else:
                    # Handle standard comparison operators
                    op_func = op_map.get(op_str, operator.eq)
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
        if self._limit is not None:
            stmt = stmt.limit(self._limit)
        if self._offset is not None:
            stmt = stmt.offset(self._offset)

        return stmt

    def build_count(self):
        stmt = select(func.count()).select_from(self.root_model)
        stmt = self._apply(stmt)
        return stmt
