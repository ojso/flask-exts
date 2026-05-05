from sqlalchemy.sql import select
from sqlalchemy import or_, and_, cast, text
from sqlalchemy.types import String
from ...datastore.sqla import db
from ..model.ajax import AjaxModelLoader, DEFAULT_PAGE_SIZE
from ...datastore.sqla.utils import get_primary_key
from ...datastore.sqla.utils import has_multiple_pks
from ...datastore.sqla.utils import is_relationship


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

        # set db.session as default session
        self.session = session if session else db.session

        self.model = model
        self.fields = options.get("fields")
        self.order_by = options.get("order_by")
        self.filters = options.get("filters")

        if not self.fields:
            raise ValueError(
                "AJAX loading requires `fields` to be specified for %s.%s"
                % (model, self.name)
            )

        self.search_fields = self._process_fields()

        if has_multiple_pks(model):
            raise NotImplementedError(
                "Current does not support multi-pk AJAX model loading."
            )

        self.pk = get_primary_key(model)

    def _process_fields(self):
        remote_fields = []
        for field in self.fields:
            if isinstance(field, str):
                attr = getattr(self.model, field, None)
                if attr is None:
                    raise ValueError("%s.%s does not exist." % (self.model, field))
                remote_fields.append(attr)
            else:
                remote_fields.append(field)
        return remote_fields

    def format(self, model):
        if not model:
            return None

        return getattr(model, self.pk), str(model)

    def get_one(self, pk):
        return self.session.get(self.model, pk)

    def get_list(self, term, offset=0, limit=DEFAULT_PAGE_SIZE):
        query = select(self.model)

        if term:
            term_filters = [
                field.cast(String).ilike(f"%{term}%") for field in self.search_fields
            ]
            query = query.filter(or_(*term_filters))

        if self.filters:
            query = query.filter(and_(*self.filters))

        if self.order_by:
            query = query.order_by(self.order_by)

        query = query.offset(offset).limit(limit)

        return self.session.execute(query).scalars().all()


def create_ajax_loader(model, session, name, field_name, options):
    attr = getattr(model, field_name, None)

    if attr is None:
        raise ValueError("Model %s does not have field %s." % (model, field_name))

    if not is_relationship(attr):
        raise ValueError("%s.%s is not a relation." % (model, field_name))

    remote_model = attr.prop.mapper.class_
    return QueryAjaxModelLoader(name, remote_model, session, **options)
