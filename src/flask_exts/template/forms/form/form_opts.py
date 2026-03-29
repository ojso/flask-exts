class FormOpts:
    __slots__ = ["widget_args"]

    def __init__(self, widget_args=None):
        self.widget_args = widget_args or {}
