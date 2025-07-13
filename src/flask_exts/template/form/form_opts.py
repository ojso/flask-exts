class FormOpts:
    __slots__ = ["widget_args", "form_rules"]

    def __init__(self, widget_args=None, form_rules=None):
        self.widget_args = widget_args or {}
        self.form_rules = form_rules
