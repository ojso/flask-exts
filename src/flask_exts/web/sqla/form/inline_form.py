from ....forms.form import Form

class InlineForm:
    """
    Settings for inline model form.

    You can use this class to customize displayed form.
    For example::

        class MyUserInlineForm(InlineForm):
            form_columns = ('name', 'email')
    """

    base_form_class = Form
    form_columns = None
    form_excluded_columns = None
    form_args = None
    form_extra_fields = None

    def __init__(self, model, **kwargs):
        """
        Constructor

        :param model:
            Model class
        :param kwargs:
            Additional options
        """
        self.model = model

        for k, v in kwargs.items():
            setattr(self, k, v)
