"""All tests for pytest-postgresql."""
import platform
import psycopg2
import pytest


QUERY = "CREATE TABLE test (id serial PRIMARY KEY, num integer, data varchar);"


@pytest.mark.skipif(
    platform.system() == 'Darwin',
    reason='These fixtures are only for linux'
)
@pytest.mark.parametrize('postgres', (
    'postgresql94',
    'postgresql95',
    'postgresql96',
    'postgresql10',
    pytest.param('postgresql11', marks=pytest.mark.xfail),
))
def test_postgresql_proc(request, postgres):
    """Test different postgresql versions."""
    postgresql_proc = request.getfixturevalue(postgres)
    assert postgresql_proc.running() is True


def test_main_postgres(postgresql):
    """Check main postgresql fixture."""
    cur = postgresql.cursor()
    cur.execute(QUERY)
    postgresql.commit()
    cur.close()


def test_two_postgreses(postgresql, postgresql2):
    """Check two postgresql fixtures on one test."""
    cur = postgresql.cursor()
    cur.execute(QUERY)
    postgresql.commit()
    cur.close()

    cur = postgresql2.cursor()
    cur.execute(QUERY)
    postgresql2.commit()
    cur.close()


def test_rand_postgres_port(postgresql_rand):
    """Check if postgres fixture can be started on random port."""
    assert postgresql_rand.status == psycopg2.extensions.STATUS_READY


def test_postgres_password(postgresql_password):
    """Check if postgres fixture can be started on random port."""
    assert postgresql_password.status == psycopg2.extensions.STATUS_READY


@pytest.mark.parametrize('_', range(2))
def test_postgres_terminate_connection(
        postgresql, _):
    """
    Test that connections are terminated between tests.

    And check that only one exists at a time.
    """
    cur = postgresql.cursor()
    cur.execute(
        'SELECT * FROM pg_stat_activity '
        'WHERE backend_type = \'client backend\';'
    )
    existing_connections = cur.fetchall()
    assert len(existing_connections) == 1, 'there is always only one connection'
    cur.close()
