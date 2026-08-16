from wtforms.fields import BooleanField


class SwitchField(BooleanField):
    """
    A wrapper field for ``BooleanField`` that renders as a Bootstrap switch.
    """

    def __init__(self, label=None, **kwargs):
        super().__init__(label, **kwargs)
