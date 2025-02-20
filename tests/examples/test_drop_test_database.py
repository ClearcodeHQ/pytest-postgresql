"""All tests for pytest-postgresql."""

from psycopg import Connection

from pytest_postgresql import factories

postgresql = factories.postgresql("postgresql_noproc")


def test_postgres_load_override(postgresql: Connection) -> None:
    """Check postgresql fixture can load one file and override database 'leftover'."""
    cur = postgresql.cursor()
    cur.execute("SELECT * FROM test;")
    results = cur.fetchall()
    assert len(results) == 1
    cur.close()
