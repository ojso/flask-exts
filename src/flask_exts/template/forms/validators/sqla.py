from flask_babel import lazy_gettext
from sqlalchemy.sql import select
from wtforms import ValidationError
from wtforms.validators import InputRequired


class Unique:
    """Checks field value unicity against specified table field.

    :param get_session:
        A function that return a SQAlchemy Session.
    :param model:
        The model to check unicity against.
    :param column:
        The unique column.
    """

    field_flags = {"unique": True}

    def __init__(self, session, model, column):
        self.session = session
        self.model = model
        self.column = column

    def __call__(self, form, field):
        # databases allow multiple NULL values for unique columns
        if field.data is None:
            return

        stmt = select(self.model).where(self.column == field.data)
        obj = self.session.execute(stmt).scalar_one_or_none()
        # if obj is None, the value is unique, and we can stop here. Otherwise, we need to check if it's the same object as the one being edited (if any).
        if obj is None:
            return
        
        # form._obj is the object being edited, if any. We should allow it to have the same value as itself.
        if not hasattr(form, "_obj") or not form._obj == obj:
            raise ValidationError(lazy_gettext("Already exists."))


class ItemsRequired(InputRequired):
    """
    A version of the ``InputRequired`` validator that works with relations,
    to require a minimum number of related items.
    """

    def __init__(self, min=1, message=None):
        super().__init__(message=message)
        self.min = min

    def __call__(self, form, field):
        items = [e for e in field.entries if not field.should_delete(e)]
        if len(items) < self.min:
            if self.message is None:
                message = field.ngettext(
                    "At least %(num)d item is required",
                    "At least %(num)d items are required",
                    self.min,
                )
            else:
                message = self.message

            raise ValidationError(message)


class TimeZoneValidator:
    """
    Tries to coerce a TimZone object from input data
    """

    def __init__(self, coerce_function):
        self.coerce_function = coerce_function

    def __call__(self, form, field):
        try:
            self.coerce_function(str(field.data))
        except Exception:
            msg = 'Not a valid timezone (e.g. "America/New_York", "Africa/Johannesburg", "Asia/Singapore").'
            raise ValidationError(field.gettext(msg))
