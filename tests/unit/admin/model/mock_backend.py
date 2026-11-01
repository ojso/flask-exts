from flask_exts.admin.model.backend import DataBackend


class MockBackend(DataBackend):
    def __init__(self, model=None, view=None, data=None, **kwargs):
        super().__init__(model, view)
        self._data = []
        # Initialize data from iterable if provided
        if data and hasattr(data, "__iter__") and not isinstance(data, str):
            # Check if data is a dict (keys are IDs)
            if isinstance(data, dict):
                for model_data in data.values():
                    # If value is a MockModel instance, convert to dict
                    if hasattr(model_data, "__dict__"):
                        model_data = {**model_data.__dict__}
                    model_instance = self.model(**model_data)
                    self._data.append(model_instance)
            else:
                # Handle list format
                for model_data in data:
                    model_instance = self.model(**model_data)
                    self._data.append(model_instance)

    def get_list(
        self,
        search=None,
        filters=None,
        sort_field=None,
        sort_desc=None,
        page=None,
        page_size=None,
    ):
        """Get paginated list of models.

        Returns dict with: total (filtered count), count (filtered count), page,
        page_size, items, page_count
        """
        # Filter by search term
        results = list(self._data)
        if search:
            search_lower = search.lower()
            results = [
                r
                for r in results
                if any(
                    search_lower in str(getattr(r, c, "")).lower()
                    for c in self.scaffold_export_columns()
                )
            ]

        # Apply filters
        if filters:
            for filter_tuple in filters:
                field_name, op, value = filter_tuple
                results = [
                    r for r in results if self._apply_filter(r, field_name, op, value)
                ]

        # Calculate total and count after filtering (same value)
        total = len(results)
        count = len(results)

        # Calculate page_count
        page_count = (
            (count + page_size - 1) // page_size if page_size and page_size > 0 else 0
        )

        # Sort
        if sort_field:
            reverse = sort_desc if sort_desc is not None else False
            results = sorted(
                results, key=lambda x: getattr(x, sort_field, ""), reverse=reverse
            )

        # Convert to dict and apply pagination
        items = [r.__dict__ for r in results]
        if page_size and page_size > 0:
            start = (page - 1) * page_size if page else 0
            items = items[start : start + page_size]

        return {
            "total": total,
            "count": count,
            "page": page,
            "page_size": page_size,
            "items": items,
            "page_count": page_count,
        }

    def get_one(self, id):
        for model in self._data:
            if model.id == id:
                return model
        return None

    def get_pk_value(self, obj):
        """Return the string representation of a record's primary key."""
        return str(obj.id)

    def _apply_filter(self, model, field_name, op, value):
        """Apply a filter to a model instance."""
        field_value = getattr(model, field_name, None)
        if op == "eq":
            return field_value == value
        elif op == "ne":
            return field_value != value
        elif op == "gt":
            return field_value > value
        elif op == "lt":
            return field_value < value
        elif op == "ge":
            return field_value >= value
        elif op == "le":
            return field_value <= value
        elif op == "in":
            return field_value in value
        elif op == "contains":
            return value in str(field_value)
        elif op == "like":
            return value.lower() in str(field_value).lower()
        return True

    def scaffold_form(self, form_type=None):
        return self.add_form()

    def scaffold_list_columns(self):
        return ["id", "col1", "col2", "col3"]

    def scaffold_display_columns(self):
        return ["id", "col1", "col2", "col3"]

    def scaffold_form_columns(self):
        return ["id", "col1", "col2", "col3"]

    def scaffold_sortable_columns(self):
        return {"col1": True, "col3": True}

    def scaffold_detail_columns(self):
        return {
            "id": lambda m: m.id,
            "col1": lambda m: m.col1,
            "col2": lambda m: m.col2,
            "col3": lambda m: m.col3,
        }

    def scaffold_export_columns(self):
        return ["id", "col1", "col2", "col3"]

    def scaffold_delete_columns(self):
        return ["id"]

    def scaffold_row_actions(self):
        def _delete(obj):
            return f"Delete {obj}"

        return {"_delete_row": _delete}

    def add_form(self):
        class AddForm:
            def __init__(self):
                self.col1 = ""
                self.col2 = ""
                self.col3 = ""

            def __call__(self, form_data):
                # Create new model
                new_model = self.model(
                    id=len(self._data) + 1,
                    col1=form_data.get("col1", ""),
                    col2=form_data.get("col2", ""),
                    col3=form_data.get("col3", ""),
                )
                self._data.append(new_model)

        return AddForm()

    def edit_form(self):
        class EditForm:
            def __init__(self):
                self.col1 = ""
                self.col2 = ""
                self.col3 = ""

            def __call__(self, form_data):
                # Update model
                for model in self._data:
                    if model.id == form_data.get("id", 0):
                        model.col1 = form_data.get("col1", "")
                        model.col2 = form_data.get("col2", "")
                        model.col3 = form_data.get("col3", "")
                return True

        return EditForm()

    def delete_form(self):
        class DeleteForm:
            def __call__(self, form_data):
                # Delete model
                id_to_delete = form_data.get("id", 0)
                for i, model in enumerate(self._data):
                    if model.id == id_to_delete:
                        self._data.pop(i)
                        return True
                return False

        return DeleteForm()

    def scaffold_filter(self, column_path: str):
        """Return filter objects for the given column path."""
        return

    def scaffold_list_form(self, validators=None):
        """Return a form class for inline editing from the list view."""

        class ListForm:
            def __init__(self):
                self.col1 = ""
                self.col2 = ""
                self.col3 = ""

            def __call__(self, form_data):
                # Update first model
                if self._data:
                    self._data[0].col1 = form_data.get("col1", "")
                    self._data[0].col2 = form_data.get("col2", "")
                    self._data[0].col3 = form_data.get("col3", "")
                return True

        return ListForm()

    def create_model(self, model):
        new_model = self.model(
            id=len(self._data) + 1,
            col1=model.col1,
            col2=model.col2,
            col3=model.col3,
        )
        self._data.append(new_model)
        return new_model

    def update_model(self, model):
        return True

    def delete_model(self, model):
        """Delete a model instance."""
        self._data.remove(model)
        return True

    def delete_model_by_pk_ids(self, ids):
        """Delete multiple records by primary key."""
        count = 0
        for model_id in ids:
            for i, model in enumerate(self._data):
                if model.id == model_id:
                    self._data.pop(i)
                    count += 1
                    break
        return count

    def get_data(self):
        return self._data
