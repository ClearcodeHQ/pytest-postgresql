"""All tests for pytest-postgresql."""

from psycopg import Connection


def test_postgres_load_one_file(postgresql: Connection) -> None:
    """Check postgresql fixture can load one file."""
    cur = postgresql.cursor()
    cur.execute("SELECT * FROM test;")
    results = cur.fetchall()
    assert len(results) == 1
    cur.close()
