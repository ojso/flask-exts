from . import db
from . import select
from .models.polymorphic import Employee, Manager, Engineer


def test_mappers():
    for mapper in db.Model.registry.mappers:
        # print(mapper.class_.__name__, mapper.local_table)
        if mapper.class_ is Employee or issubclass(mapper.class_, Employee):
            assert mapper.polymorphic_on.name == "type"
            assert mapper.class_.__tablename__ == "employee"
            assert mapper.local_table.name == "employee"


def test_create_table(app):
    with app.app_context():
        db.create_all()
        db.session.add_all(
            [
                Manager(
                    name="Mr. Krabs",
                    manager_name="Eugene H. Krabs",
                ),
                Engineer(name="SpongeBob", engineer_info="Krabby Patty Master"),
                Engineer(
                    name="Squidward",
                    engineer_info="Senior Customer Engagement Engineer",
                ),
            ]
        )
        db.session.commit()
        stmt = select(Engineer)
        # print(stmt)
        assert "where employee.type" in str(stmt).lower()
        engineers = db.session.execute(stmt).scalars()
        for e in engineers:
            # print(e.name, e.type)
            assert isinstance(e, Engineer)
            assert e.type == "engineer"
