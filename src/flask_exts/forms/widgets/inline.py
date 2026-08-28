from wtforms.widgets import ListWidget
from wtforms.widgets import TableWidget


class InlineFieldListWidget(ListWidget):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.template = "inline_field_list"


class InlineFormWidget(TableWidget):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.template = "inline_form"
