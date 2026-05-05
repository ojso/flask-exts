from wtforms.validators import ValidationError
from wtforms.fields import SelectFieldBase
from ..widgets import AjaxSelect2Widget


class AjaxSelectField(SelectFieldBase):
    """
    Ajax Model Select Field
    """

    widget = AjaxSelect2Widget()

    separator = ","

    def __init__(
        self,
        loader,
        label=None,
        validators=None,
        allow_blank=False,
        blank_text="",
        **kwargs,
    ):
        super().__init__(label, validators, **kwargs)
        self.loader = loader

        self.allow_blank = allow_blank
        self.blank_text = blank_text

    @property
    def data(self):
        if self._formdata:
            model = self.loader.get_one(self._formdata)
            if model is not None:
                self._data = model
                self._formdata = None

        return self._data
    
    @data.setter
    def data(self, value):
        self._data = value
        self._formdata = None


    def _format_item(self, item):
        value = self.loader.format(self.data)
        return (value[0], value[1], True)

    def process_formdata(self, valuelist):
        if valuelist:
            if self.allow_blank and valuelist[0] == "__None":
                self.data = None
            else:
                self._data = None
                self._formdata = valuelist[0]

    def pre_validate(self, form):
        if not self.allow_blank and self.data is None:
            raise ValidationError(self.gettext("Not a valid choice"))


class AjaxSelectMultipleField(AjaxSelectField):
    """
    Ajax-enabled model multi-select field.
    """

    widget = AjaxSelect2Widget(multiple=True)

    def __init__(self, loader, label=None, validators=None, default=None, **kwargs):
        if default is None:
            default = []

        super().__init__(loader, label, validators, default=default, **kwargs)
        self._invalid_formdata = False

    @property
    def data(self):
        formdata = self._formdata
        if formdata:
            data = []

            # TODO: Optimize?
            for item in formdata:
                model = self.loader.get_one(item) if item else None
                if model:
                    data.append(model)
                else:
                    self._invalid_formdata = True
            self._data = data
            self._formdata = None

        return self._data

    @data.setter
    def data(self, value):
        self._data = value
        self._formdata = None


    def process_formdata(self, valuelist):
        self._formdata = set()

        for field in valuelist:
            for n in field.split(self.separator):
                self._formdata.add(n)

    def pre_validate(self, form):
        if self._invalid_formdata:
            raise ValidationError(self.gettext("Not a valid choice"))
