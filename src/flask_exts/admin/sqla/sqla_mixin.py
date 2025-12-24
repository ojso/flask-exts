from ...datastore.sqla.utils import get_model_mapper
from ...datastore.sqla.utils import get_primary_key
from ...datastore.sqla.utils import instance_primary_key_value
from ...datastore.sqla.utils import stmt_delete_model_pk_ids



class SqlaMixin:
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def scaffold_pk(self):
        """
        Return primary key name from a model. If the primary key consists of multiple columns,
        return the corresponding tuple
        """
        self._primary_key = get_primary_key(self.model)

    def has_multiple_pks(self):
        return isinstance(self._primary_key, tuple)
    
    def get_primary_key_value(self, instance):
        """
        Return primary key values from an instance.
        """
        return instance_primary_key_value(instance)

    def delete_pk_ids(self, ids: list):
        """
        Return a delete statement that deletes all rows with primary key in ids
        """
        stmt = stmt_delete_model_pk_ids(self.model, ids)
        result = self.session.execute(stmt)
        self.session.commit()
        return result
    
    def _get_model_iterator(self, model=None):
        """
        Return property iterator for the model
        """
        if model is None:
            model = self.model

        return get_model_mapper(model).attrs
    
