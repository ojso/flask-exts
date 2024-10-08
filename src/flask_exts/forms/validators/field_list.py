from wtforms.validators import StopValidation

class FieldListInputRequired:
    """Validates that at least one item was provided for a FieldList"""

    field_flags = ("required",)

    def __call__(self, form, field):
        if len(field.entries) == 0:
            field.errors[:] = []
            raise StopValidation(field.gettext("This field requires at least one item."))
