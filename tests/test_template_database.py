"""Template database tests."""
import pytest
from psycopg import Connection

from pytest_postgresql.factories import postgresql, postgresql_proc
from tests.loader import load_database

postgresql_proc_with_template = postgresql_proc(
    port=21987,
    dbname="stories_templated",
    load=[load_database],
)

postgresql_template = postgresql(
    "postgresql_proc_with_template",
    dbname="stories_templated",
)


@pytest.mark.parametrize("_", range(5))
def test_template_database(postgresql_template: Connection, _: int) -> None:
    """Check that the database structure gets recreated out of a template."""
    with postgresql_template.cursor() as cur:
        cur.execute("SELECT * FROM stories")
        res = cur.fetchall()
        assert len(res) == 4
        cur.execute("TRUNCATE stories")
        cur.execute("SELECT * FROM stories")
        res = cur.fetchall()
        assert len(res) == 0
