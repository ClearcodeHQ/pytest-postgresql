"""All tests for pytest-postgresql."""
import psycopg2
import pytest


MAKE_Q = "CREATE TABLE test (id serial PRIMARY KEY, num integer, data varchar);"
SELECT_Q = "SELECT * FROM test;"


@pytest.mark.parametrize('postgres', (
    'postgresql95',
    'postgresql96',
    'postgresql10',
    'postgresql11',
    'postgresql12',
    'postgresql13'
))
def test_postgresql_proc(request, postgres):
    """Test different postgresql versions."""
    postgresql_proc = request.getfixturevalue(postgres)
    assert postgresql_proc.running() is True


def test_main_postgres(postgresql):
    """Check main postgresql fixture."""
    cur = postgresql.cursor()
    cur.execute(MAKE_Q)
    postgresql.commit()
    cur.close()


def test_two_postgreses(postgresql, postgresql2):
    """Check two postgresql fixtures on one test."""
    cur = postgresql.cursor()
    cur.execute(MAKE_Q)
    postgresql.commit()
    cur.close()

    cur = postgresql2.cursor()
    cur.execute(MAKE_Q)
    postgresql2.commit()
    cur.close()


def test_postgres_load_one_file(postgresql_load_1):
    """Check postgresql fixture can load one file."""
    cur = postgresql_load_1.cursor()
    cur.execute(SELECT_Q)
    results = cur.fetchall()
    assert len(results) == 1
    cur.close()


def test_postgres_load_two_files(postgresql_load_2):
    """Check postgresql fixture can load two files."""
    cur = postgresql_load_2.cursor()
    cur.execute(SELECT_Q)
    results = cur.fetchall()
    assert len(results) == 2
    cur.close()


def test_rand_postgres_port(postgresql_rand):
    """Check if postgres fixture can be started on random port."""
    assert postgresql_rand.status == psycopg2.extensions.STATUS_READY


@pytest.mark.parametrize('_', range(2))
def test_postgres_terminate_connection(
        postgres10, _):
    """
    Test that connections are terminated between tests.

    And check that only one exists at a time.
    """
    cur = postgres10.cursor()
    cur.execute(
        'SELECT * FROM pg_stat_activity '
        'WHERE backend_type = \'client backend\';'
    )
    existing_connections = cur.fetchall()
    assert len(existing_connections) == 1, 'there is always only one connection'
    cur.close()
