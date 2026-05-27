from ..model.ajax import AjaxModelLoader, DEFAULT_PAGE_SIZE
from .query import Query

class QueryAjaxModelLoader(AjaxModelLoader):
    def __init__(self, name, model, session=None, **options):
        """
        Constructor.

        :param fields:
            Fields to run query against
        :param filters:
            Additional filters to apply to the loader
        """
        super().__init__(name, options)

        self.session = session
        self.model = model
        self.search_fields = options.get("fields")
        self.order_by = options.get("order_by")
        self.filters = options.get("filters")
        self.pk = Query.get_model_primary_key(model)

    def format(self, model):
        if not model:
            return None
        return getattr(model, self.pk), str(model)

    def get_one(self, pk):
        return self.session.get(self.model, pk)

    def get_list(self, term, offset=0, limit=DEFAULT_PAGE_SIZE):
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
    return QueryAjaxModelLoader(name, remote_model, session, **options)
