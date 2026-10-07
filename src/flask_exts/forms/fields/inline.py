from wtforms.fields import Field
from wtforms.utils import unset_value

from ...datastore.sqla.utils import get_model_primary_key
from ..widgets.inline import InlineModelWidget


class InlineModelField(Field):
    """Relationship field rendered and persisted by the inline-model AJAX UI."""

    widget = InlineModelWidget()

    def __init__(
        self,
        form_class,
        model,
        relationship_name,
        is_collection,
        inline_view,
        **kwargs,
    ):
        super().__init__(**kwargs)
        self.form_class = form_class
        self.model = model
        self.relationship_name = relationship_name
        self.is_collection = is_collection
        self.inline_view = inline_view
        self.form_opts = {
            "widget_args": getattr(inline_view, "form_widget_args", None)
        }

    def process(self, formdata, data=unset_value, extra_filters=None):
        value = None if data is unset_value else data
        self.object_data = value
        if self.is_collection:
            self.data = list(value or ())
        else:
            self.data = value

    def populate_obj(self, obj, name):
        # Inline objects are saved independently through the AJAX endpoint.
        return

    def get_pk(self, obj):
        primary_key = get_model_primary_key(self.model)
        if isinstance(primary_key, tuple):
            return [getattr(obj, key) for key in primary_key]
        return getattr(obj, primary_key)

    def get_prefix(self, index):
        return f"{self.name}-{index}-"
