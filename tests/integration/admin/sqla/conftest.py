import pytest

from flask_exts.admin.sqla.view import SqlaModelView


class MockSqlaView(SqlaModelView):
    def __init__(
        self,
        model,
        name=None,
        endpoint=None,
        url=None,
        **kwargs,
    ):
        for k, v in kwargs.items():
            setattr(self, k, v)
        self.form_choices = {"choice_field": [("choice-1", "One"), ("choice-2", "Two")]}
        super().__init__(model, name=name, endpoint=endpoint, url=url)


@pytest.fixture
def sqla_view_factory():
    return MockSqlaView
