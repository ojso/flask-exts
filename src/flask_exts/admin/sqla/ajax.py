from ...datastore.sqla.query import Query
from ...datastore.sqla.utils import get_model_primary_key
from ..model.ajax import DEFAULT_PAGE_SIZE, AjaxModelLoader


class AjaxSqlaModelLoader(AjaxModelLoader):
    def __init__(self, name, model, session=None, **options):
        """
        Constructor.

        Args:
            name:
                Field name
            fields:
                Fields to run query against
            filters:
                Additional filters to apply to the loader
        """
        super().__init__(name, options)
        self.model = model
        self.session = session
        self.search_fields = options.get("fields")
        self.order_by = options.get("order_by")
        self.filters = options.get("filters")
        self.pk = get_model_primary_key(model)

    def format(self, model):
        """
        Return (id, name) tuple from the model.
        """
        if not model:
            return None
        return getattr(model, self.pk), str(model)

    def get_one(self, pk):
        """
        Find model by its primary key.

        Args:
            pk:
                Primary key value
        """
        return self.session.get(self.model, pk)

    def get_list(self, term, offset=0, limit=DEFAULT_PAGE_SIZE):
        """
        Return models that match `query`.

        Args:
            view:
                Administrative view.
            query:
                Query string
            offset:
                Offset
            limit:
                Limit
        """
        query = Query(self.model)

        if term:
            query.add_search_term(term, self.search_fields)

        if self.filters:
            for filter in self.filters:
                query.add_filter(filter)

        if self.order_by:
            query.add_order_by(self.order_by)

        query.offset(offset)
        query.limit(limit)
        stmt = query.build()
        result = self.session.execute(stmt).scalars().all()
        return result


def create_ajax_loader(model, session, name, field_name, options):
    attr = getattr(model, field_name, None)
    remote_model = attr.prop.mapper.class_
    return AjaxSqlaModelLoader(name, remote_model, session, **options)
