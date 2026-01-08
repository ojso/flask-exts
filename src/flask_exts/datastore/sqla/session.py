from sqlalchemy.orm import Session


class MultSession(Session):
    def __init__(self, db, **kwargs):
        super().__init__(**kwargs)
        self._db = db

    def get_bind(
        self,
        mapper=None,
        clause=None,
        bind=None,
        **kwargs,
    ):
        return super().get_bind(mapper=mapper, clause=clause, bind=bind, **kwargs)
