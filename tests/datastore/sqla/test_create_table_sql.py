from sqlalchemy.schema import CreateTable
from sqlalchemy import create_mock_engine
from .models.demo import Demo


def mock_engine_for_dialect(dialect_name: str):
    if dialect_name == "postgresql":
        url = "postgresql:///"
    elif dialect_name == "sqlite":
        url = "sqlite:///"
    elif dialect_name == "mysql":
        url = "mysql:///"
    else:
        raise ValueError("Unsupported dialect")

    def dump(sql, *multiparams, **params):
        print(sql.compile(dialect=engine.dialect))

    engine = create_mock_engine(url, dump)
    return engine



class TestCreateTableSQL:
    def test_create_table_sql(self):
        engine = mock_engine_for_dialect("postgresql")
        # metadata.create_all(engine, checkfirst=False)
        # print(CreateTable(Demo.__table__))
        print(CreateTable(Demo.__table__).compile(engine))

    