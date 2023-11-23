"""Template database tests."""
import pytest
from psycopg import Connection

from pytest_postgresql.factories import postgresql, postgresql_proc
from tests.loader import load_database

postgresql_proc_with_template_for_session = postgresql_proc(
    port=21987,
    dbname="session_template",
    load=[load_database],
)

postgresql_template_function = postgresql(
    "postgresql_proc_with_template_for_session"
)

postgresql_template_session = postgresql(
    "postgresql_proc_with_template_for_session",
    target_dbname="some_unique_name",
    scope="session",
)

# the two tests will use the same template DB, though one uses a session scoped fixture to setup
# additional data to be shared between some tests. Because this db will live the entire 
# session, it needs to have a special name that will not conflict with others. This allows
# reusing the template database also in session scoped fixtures.

@pytest.fixture(scope="session")
def add_story(postgresql_template_session: Connection) -> Connection:
    with postgresql_template_session.cursor() as cur:
        cur.execute("INSERT INTO stories (name) VALUES ('Prince Caspian')")
        postgresql_template_session.commit()


@pytest.mark.parametrize("_", range(5))
def test_function_scoped_client_fixture(postgresql_template_function: Connection, _: int) -> None:
    """Check that the database structure gets recreated out of the template."""
    with postgresql_template_function.cursor() as cur:
        cur.execute("SELECT * FROM stories")
        res = cur.fetchall()
        assert len(res) == 4


@pytest.mark.parametrize("_", range(5))
def test_session_scoped_client_fixture(add_story: Connection, _: int) -> None:
    """Check that the database structure gets recreated out of the template."""
    with postgresql_template_session.cursor() as cur:
        cur.execute("SELECT * FROM stories")
        res = cur.fetchall()
        assert len(res) == 5