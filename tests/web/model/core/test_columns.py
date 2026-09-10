from flask_exts.web.model.view import ModelView


class MockModel:
    def __init__(self, id=None, c1=1, c2=2, c3=3):
        self.id = id
        self.col1 = c1
        self.col2 = c2
        self.col3 = c3


class MockModelView(ModelView):
    column_list = ["col1", "col3"]
    column_labels = {"col1": "Column1"}


def test_get_column_label():
    view = MockModelView(MockModel)
    assert view.get_column_label("col1") == "Column1"
