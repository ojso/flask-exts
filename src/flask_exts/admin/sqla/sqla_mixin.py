from sqlalchemy import inspect
# https://docs.sqlalchemy.org/en/20/orm/mapping_styles.html#orm-mapper-inspection-mapper
class SqlaMixin:
    def has_multiple_pks(self, model=None):
        """
            Return True, if the model has more than one primary key
        """
        if model is None:
            model = self.model
        return len(model._sa_class_manager.mapper.primary_key) > 1
    
    def get_primary_key(self):
        """
            Return primary key name from a model. If the primary key consists of multiple columns,
            return the corresponding tuple
        """
        insp = inspect(self.model)

        mapper = model._sa_class_manager.mapper
        pks = [mapper.get_property_by_column(c).key for c in mapper.primary_key]
        if len(pks) == 1:
            return pks[0]
        elif len(pks) > 1:
            return tuple(pks)
        else:
            return None