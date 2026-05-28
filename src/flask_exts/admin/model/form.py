import types

from ...template.forms.form.base_form import BaseForm


def convert_formfield(*args):
    def decorator(func):
        func._converter_for_formfield = args
        return func

    return decorator


class BaseFormFieldConverter:
    _converters = {}

    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)
        converters = {}
        for base in cls.__bases__:
            base_map = getattr(base, "_converters", {})
            converters.update(base_map)
        for name, method in cls.__dict__.items():
            if callable(method) and hasattr(method, "_converter_for_formfield"):
                for type_name in method._converter_for_formfield:
                    converters[type_name] = method
        cls._converters = converters

    def __init__(self, use_mro=True):
        self.use_mro = use_mro

    def get_converter(self, column):
        col_type = type(column.type)
        if self.use_mro:
            types_list = col_type.__mro__
        else:
            types_list = (col_type,)

        # Search by module + name
        for t in types_list:
            full_name = f"{t.__module__}.{t.__name__}"
            if full_name in self._converters:
                func = self._converters[full_name]
                return types.MethodType(func, self)

        # Search by name
        for t in types_list:
            short_name = t.__name__
            if short_name in self._converters:
                func = self._converters[short_name]
                return types.MethodType(func, self)

        return None

    def get_form(
        self, model, base_class=BaseForm, only=None, exclude=None, field_args=None
    ):
        raise NotImplementedError()




class InlineBaseFormAdmin:
    """
    Settings for inline form administration.

    You can use this class to customize displayed form.
    For example::

        class MyUserInfoForm(InlineBaseFormAdmin):
            form_columns = ('name', 'email')
    """

    _defaults = [
        "form_base_class",
        "form_columns",
        "form_excluded_columns",
        "form_args",
        "form_extra_fields",
    ]

    def __init__(self, **kwargs):
        """
        Constructor

        :param kwargs:
            Additional options
        """
        for k in self._defaults:
            if not hasattr(self, k):
                setattr(self, k, None)

        for k, v in kwargs.items():
            setattr(self, k, v)

    def get_form(self):
        """
        If you want to use completely custom form for inline field, you can override
        form generation logic by overriding this method and returning your form.
        """
        return None

    def postprocess_form(self, form_class):
        """
        Post process form. Use this to contribute fields.

        For example::

            class MyInlineForm(InlineFormAdmin):
                def postprocess_form(self, form):
                    form.value = StringField('value')
                    return form

            class MyAdmin(ModelView):
                inline_models = (MyInlineForm(ValueModel),)
        """
        return form_class


class InlineFormAdmin(InlineBaseFormAdmin):
    """
    Settings for inline form administration. Used by relational backends (SQLAlchemy, Peewee), where model
    class can not be inherited from the parent model definition.
    """

    def __init__(self, model, **kwargs):
        """
        Constructor

        :param model:
            Model class
        """
        self.model = model

        super().__init__(**kwargs)


class InlineModelConverterBase:
    form_admin_class = InlineFormAdmin

    def __init__(self, view):
        """
        Base constructor

        :param view:
            View class
        """
        self.view = view

    def get_label(self, info, name):
        """
        Get inline model field label

        :param info:
            Inline model info
        :param name:
            Field name
        """
        form_name = getattr(info, "form_label", None)
        if form_name:
            return form_name

        column_labels = getattr(self.view, "column_labels", None)

        if column_labels and name in column_labels:
            return column_labels[name]

        return None

    def get_info(self, p):
        """
        Figure out InlineFormAdmin information.

        :param p:
            Inline model. Can be one of:

             - ``tuple``, first value is related model instance,
             second is dictionary with options
             - ``InlineFormAdmin`` instance
             - Model class
        """
        if isinstance(p, tuple):
            return self.form_admin_class(p[0], **p[1])
        elif isinstance(p, self.form_admin_class):
            return p

        return None
