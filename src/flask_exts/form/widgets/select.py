from wtforms.widgets import Select
from wtforms.widgets import TextInput


class Select2Widget(Select):
    """Select2 Widget."""

    def __call__(self, field, **kwargs):
        kwargs.setdefault("data-role", "select2")
        allow_blank = getattr(field, "allow_blank", False)
        if allow_blank and not self.multiple:
            kwargs["data-allow-blank"] = "1"

        return super().__call__(field, **kwargs)


class Select2TagsWidget(TextInput):
    """Select2Tags Widget."""

    def __call__(self, field, **kwargs):
        kwargs.setdefault("data-role", "select2-tags")
        kwargs.setdefault(
            "data-allow-duplicate-tags",
            "true" if getattr(field, "allow_duplicates", False) else "false",
        )
        return super().__call__(field, **kwargs)
