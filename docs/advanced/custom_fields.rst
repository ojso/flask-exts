Custom Form Fields and Validators
===================================

English / 中文
----------------
This page is provided in English with a Chinese summary for easier reading.
中文说明：本页面保留英文原文，并附带中文说明，便于中英文对照阅读。


Flask-Exts provides extensive support for creating custom form fields and validators to meet your specific requirements.

Creating Custom Form Fields
-----------------------------

Understanding Field Structure
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

A form field in WTForms consists of:

1. **Field class**: Handles data processing and validation
2. **Widget class**: Handles HTML rendering
3. **Validators**: Validate the input data

Basic Custom Field
~~~~~~~~~~~~~~~~~~~

Here's a simple example of a custom color picker field::

    from wtforms import Field
    from wtforms.widgets import html_params, HTMLString
    from wtforms.validators import DataRequired

    class ColorPickerWidget:
        def __call__(self, field, **kwargs):
            return HTMLString(
                '<input type="color" id="%s" name="%s" value="%s" %s>' % (
                    field.id,
                    field.name,
                    field.data or '#000000',
                    html_params(**kwargs)
                )
            )

    class ColorPickerField(Field):
        widget = ColorPickerWidget()

        def _value(self):
            if self.data:
                return self.data
            return '#000000'

Using the Custom Field
~~~~~~~~~~~~~~~~~~~~~~

Use your custom field in forms::

    from flask_exts.forms.form import FlaskForm
    from wtforms import StringField

    class BrandingForm(FlaskForm):
        name = StringField('Brand Name', [DataRequired()])
        primary_color = ColorPickerField('Primary Color')
        secondary_color = ColorPickerField('Secondary Color')

Advanced Custom Field Example
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

A more complex example with data conversion and validation::

    from wtforms import Field
    from wtforms.validators import ValidationError, Regexp
    import json

    class JSONField(Field):
        """A field that stores JSON data"""
        widget = TextArea()

        def _value(self):
            if self.data:
                return json.dumps(self.data, indent=2)
            return ''

        def process_data(self, value):
            if value is None:
                self.data = {}
            elif isinstance(value, str):
                try:
                    self.data = json.loads(value)
                except json.JSONDecodeError:
                    self.data = {}
            else:
                self.data = value

        def process_form_data(self, valuelist):
            if valuelist:
                try:
                    self.data = json.loads(valuelist[0])
                except json.JSONDecodeError:
                    raise ValidationError('Invalid JSON data')

Field with Custom Processing
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Handle complex data processing::

    from datetime import datetime

    class DateRangeField(Field):
        """A field that stores start and end dates"""

        def process_data(self, value):
            if value is None:
                self.data = {'start': None, 'end': None}
            elif isinstance(value, dict):
                self.data = value
            else:
                self.data = {'start': None, 'end': None}

        def process_form_data(self, valuelist):
            if len(valuelist) >= 2:
                try:
                    self.data = {
                        'start': datetime.strptime(valuelist[0], '%Y-%m-%d').date(),
                        'end': datetime.strptime(valuelist[1], '%Y-%m-%d').date(),
                    }
                except ValueError:
                    raise ValidationError('Invalid date format')

Creating Custom Validators
----------------------------

Basic Custom Validator
~~~~~~~~~~~~~~~~~~~~~~

Create a reusable validator::

    from wtforms.validators import ValidationError

    class FileExtensionValidator:
        """Validate file extension"""
        def __init__(self, allowed_extensions, message='Invalid file extension'):
            self.allowed_extensions = allowed_extensions
            self.message = message

        def __call__(self, form, field):
            if field.data:
                # Get filename
                filename = field.data.filename
                if not self._is_allowed(filename):
                    raise ValidationError(self.message)

        def _is_allowed(self, filename):
            return '.' in filename and \
                   filename.rsplit('.', 1)[1].lower() in self.allowed_extensions

Using Custom Validators
~~~~~~~~~~~~~~~~~~~~~~~~

Use validators in form fields::

    from flask_exts.forms.form import FlaskForm
    from wtforms import FileField

    class DocumentUploadForm(FlaskForm):
        document = FileField('Upload Document', [
            FileExtensionValidator(['pdf', 'doc', 'docx'])
        ])

Database-Dependent Validators
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Validate against database data::

    from flask_exts.proxies import _datastore

    class UniqueEmailValidator:
        """Ensure email is unique in database"""
        def __init__(self, message='Email already registered'):
            self.message = message

        def __call__(self, form, field):
            user = _datastore.find_user(email=field.data)
            if user:
                raise ValidationError(self.message)

Chaining Validators
~~~~~~~~~~~~~~~~~~~

Combine multiple validators::

    from wtforms.validators import Length, Regexp, DataRequired

    class PasswordField(Field):
        widget = PasswordInput()

        validators = [
            DataRequired('Password is required'),
            Length(min=8, message='Password must be at least 8 characters'),
            Regexp(
                r'^(?=.*[A-Za-z])(?=.*\d)(?=.*[@$!%*#?&])[A-Za-z\d@$!%*#?&]{8,}$',
                message='Password must contain letters, numbers, and special characters'
            ),
        ]

Conditional Validators
~~~~~~~~~~~~~~~~~~~~~~

Apply validators conditionally::

    class ConditionalRequiredValidator:
        """Make field required if condition is true"""
        def __init__(self, condition, message='Field is required'):
            self.condition = condition
            self.message = message

        def __call__(self, form, field):
            if self.condition(form):
                if not field.data:
                    raise ValidationError(self.message)

Advanced Patterns
-----------------

Cross-Field Validation
~~~~~~~~~~~~~~~~~~~~~~

Validate based on multiple fields::

    class MatchingFieldsValidator:
        """Ensure two fields match"""
        def __init__(self, other_field_name, message='Fields do not match'):
            self.other_field_name = other_field_name
            self.message = message

        def __call__(self, form, field):
            other = form[self.other_field_name]
            if field.data != other.data:
                raise ValidationError(self.message)

    # Usage
    class PasswordChangeForm(FlaskForm):
        new_password = StringField('New Password')
        confirm_password = StringField('Confirm Password', [
            MatchingFieldsValidator('new_password')
        ])

Async Field Processing
~~~~~~~~~~~~~~~~~~~~~~

Handle asynchronous field processing::

    from wtforms import Field
    import asyncio

    class AsyncValidatorField(Field):
        def __init__(self, label=None, validators=None, async_validator=None, **kwargs):
            super().__init__(label, validators, **kwargs)
            self.async_validator = async_validator

        async def validate_async(self):
            if self.async_validator:
                await self.async_validator(self.data)

Dynamic Field Validators
~~~~~~~~~~~~~~~~~~~~~~~~~

Add validators dynamically based on context::

    class DynamicValidatorField(Field):
        def __init__(self, *args, **kwargs):
            self.dynamic_validators = []
            super().__init__(*args, **kwargs)

        def add_validator(self, validator):
            self.dynamic_validators.append(validator)

        def validate(self, form, extra_validators=()):
            all_validators = tuple(self.dynamic_validators) + \
                           tuple(self.validators) + \
                           extra_validators
            super().validate(form, all_validators)

Integration with Admin
----------------------

Using Custom Fields in Admin Views
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Custom fields work seamlessly with admin views::

    from flask_exts.admin.sqla.view import SqlaModelView

    class ProductView(SqlaModelView):
        form_columns = ['name', 'price', 'metadata', 'color']
        form_args = {
            'metadata': {
                'field_class': JSONField,
                'label': 'Product Metadata'
            },
            'color': {
                'field_class': ColorPickerField,
                'label': 'Primary Color'
            }
        }

Field Type Conversion
~~~~~~~~~~~~~~~~~~~~~

Automatically convert between Python types and form representations::

    class CurrencyField(Field):
        """Convert between float and currency string"""

        def _value(self):
            if self.data:
                return f"${self.data:.2f}"
            return "$0.00"

        def process_data(self, value):
            self.data = float(value) if value else 0.0

        def process_form_data(self, valuelist):
            if valuelist:
                # Remove currency symbol and convert
                value = valuelist[0].replace('$', '').replace(',', '')
                try:
                    self.data = float(value)
                except (ValueError, TypeError):
                    self.data = 0.0

Best Practices
--------------

1. **Keep it simple**: Complex fields are hard to test and maintain
2. **Provide clear error messages**: Help users understand what went wrong
3. **Handle edge cases**: Null values, empty strings, invalid formats
4. **Test thoroughly**: Unit test all field logic
5. **Document well**: Explain usage and configuration options
6. **Reuse existing validators**: Don't reinvent the wheel
7. **Consider performance**: Avoid expensive operations in validators
8. **Make fields composable**: Support stacking and combining validators

Common Field Types to Create
-----------------------------

- **Color picker**: RGB/Hex color selection
- **Date range picker**: Select start and end dates
- **Tag input**: Comma-separated or structured tags
- **Markdown editor**: With preview
- **Code editor**: With syntax highlighting
- **File uploader**: Drag-and-drop or browse
- **Image cropper**: Crop and resize images
- **Signature pad**: Capture signatures
- **Phone number**: With country code support
- **Currency**: With locale-specific formatting

Troubleshooting
---------------

Field not rendering
~~~~~~~~~~~~~~~~~~~

- Verify widget class is set
- Check HTML output for errors
- Verify template includes field
- Check browser console for JavaScript errors

Validation not working
~~~~~~~~~~~~~~~~~~~~~~

- Ensure validators are passed to field
- Check validator order (important for conditional logic)
- Verify validator messages are set
- Test validators independently

Data not persisting
~~~~~~~~~~~~~~~~~~~

- Verify ``process_data()`` is implemented correctly
- Check ``process_form_data()`` handles all cases
- Ensure database column type matches field type
- Verify form population from model

See Also
--------

- :doc:`../api` - Field API reference
- `WTForms documentation <https://wtforms.readthedocs.io/>`_
- :doc:`modelview` - modelview configuration
- ``flask_exts.forms`` - Forms module source
