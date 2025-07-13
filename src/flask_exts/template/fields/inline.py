import itertools
from wtforms.fields import FieldList, FormField
from wtforms.utils import unset_value
from ..widgets.inline import InlineFieldListWidget
from ..widgets.inline import InlineFormWidget


class InlineFieldList(FieldList):
    widget = InlineFieldListWidget()

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def __call__(self, **kwargs):
        # Create template
        meta = getattr(self, "meta", None)
        if meta:
            template = self.unbound_field.bind(form=None, name="", _meta=meta)
        else:
            template = self.unbound_field.bind(form=None, name="")
        # Small hack to remove separator from FormField
        if isinstance(template, FormField):
            template.separator = ""

        template.process(None)

        return self.widget(
            self, template=template, check=self.display_row_controls, **kwargs
        )

    def display_row_controls(self, field):
        return True

    def process(self, formdata, data=unset_value, extra_filters=None):
        res = super().process(formdata, data)

        # Postprocess - contribute flag
        if formdata:
            for f in self.entries:
                key = "del-%s" % f.id
                f._should_delete = key in formdata

        return res

    def validate(self, form, extra_validators=tuple()):
        """
        Validate this FieldList.

        Note that FieldList validation differs from normal field validation in
        that FieldList validates all its enclosed fields first before running any
        of its own validators.
        """
        self.errors = []

        # Run validators on all entries within
        for subfield in self.entries:
            if not self.should_delete(subfield) and not subfield.validate(form):
                self.errors.append(subfield.errors)

        chain = itertools.chain(self.validators, extra_validators)
        self._run_validation_chain(form, chain)

        return len(self.errors) == 0

    def should_delete(self, field):
        return getattr(field, "_should_delete", False)

    def populate_obj(self, obj, name):
        values = getattr(obj, name, None)
        try:
            ivalues = iter(values)
        except TypeError:
            ivalues = iter([])

        candidates = itertools.chain(ivalues, itertools.repeat(None))
        _fake = type(str("_fake"), (object,), {})

        output = []
        for field, data in zip(self.entries, candidates):
            if not self.should_delete(field):
                fake_obj = _fake()
                fake_obj.data = data
                field.populate_obj(fake_obj, "data")
                output.append(fake_obj.data)

        setattr(obj, name, output)


class InlineFormField(FormField):
    """
    Inline version of the ``FormField`` widget.
    """

    widget = InlineFormWidget()


class InlineModelFormField(FormField):
    """
    Customized ``FormField``.

    Excludes model primary key from the `populate_obj` and
    handles `should_delete` flag.
    """

    widget = InlineFormWidget()

    def __init__(self, form_class, pk, form_opts=None, **kwargs):
        super().__init__(form_class, **kwargs)

        self._pk = pk
        self.form_opts = form_opts

    def get_pk(self):

        if isinstance(self._pk, (tuple, list)):
            return tuple(getattr(self.form, pk).data for pk in self._pk)

        return getattr(self.form, self._pk).data

    def populate_obj(self, obj, name):
        for name, field in self.form._fields.items():
            if name != self._pk:
                field.populate_obj(obj, name)
