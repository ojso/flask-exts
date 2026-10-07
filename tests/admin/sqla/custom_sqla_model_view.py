from flask_exts.admin.sqla.view import SqlaModelView


class CustomSqlaModelView(SqlaModelView):
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

        super().__init__(model, name=name, endpoint=endpoint, url=url)

    form_choices = {"choice_field": [("choice-1", "One"), ("choice-2", "Two")]}
