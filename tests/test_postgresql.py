"""All tests for pytest-postgresql."""
import psycopg2
import pytest

from pytest_postgresql import factories

query = "CREATE TABLE test (id serial PRIMARY KEY, num integer, data varchar);"

pg_ctl = '/usr/lib/postgresql/{ver}/bin/pg_ctl'

postgresql92 = factories.postgresql_proc(pg_ctl.format(ver='9.2'), port=None)
postgresql93 = factories.postgresql_proc(pg_ctl.format(ver='9.3'), port=None)
postgresql94 = factories.postgresql_proc(pg_ctl.format(ver='9.4'), port=None)
postgresql95 = factories.postgresql_proc(pg_ctl.format(ver='9.5'), port=None)
postgresql96 = factories.postgresql_proc(pg_ctl.format(ver='9.6'), port=None)
postgresql10 = factories.postgresql_proc(pg_ctl.format(ver='10'), port=None)
postgresql101 = factories.postgresql_proc(pg_ctl.format(ver='10.1'), port=None)


@pytest.mark.parametrize('postgres', (
    'postgresql92',
    'postgresql93',
    'postgresql94',
    'postgresql95',
    'postgresql96',
    pytest.param('postgresql10', marks=pytest.mark.xfail),
    pytest.param('postgresql101', marks=pytest.mark.xfail),
))
def test_postgresql_proc(request, postgres):
    """Test different postgresql versions."""
    postgresql_proc = request.getfixturevalue(postgres)
    assert postgresql_proc.running() is True


def test_main_postgres(postgresql):
    """Check main postgresql fixture."""
    cur = postgresql.cursor()
    cur.execute(query)
    postgresql.commit()
    cur.close()


postgresql_proc2 = factories.postgresql_proc(port=9876)
postgresql2 = factories.postgresql('postgresql_proc2')


def test_two_postgreses(postgresql, postgresql2):
    """Check two postgresql fixtures on one test."""
    cur = postgresql.cursor()
    cur.execute(query)
    postgresql.commit()
    cur.close()

    cur = postgresql2.cursor()
    cur.execute(query)
    postgresql2.commit()
    cur.close()


postgresql_rand_proc = factories.postgresql_proc(port=None)
postgresql_rand = factories.postgresql('postgresql_rand_proc')


def test_rand_postgres_port(postgresql_rand):
    """Check if postgres fixture can be started on random port."""
    assert postgresql_rand.status == psycopg2.extensions.STATUS_READY


@pytest.mark.parametrize('run', range(2))
def test_postgres_terminate_connection(
        postgresql, run):
    """
    Test that connections are terminated between tests.

    And check that only one exists at a time.
    """
    cur = postgresql.cursor()
    cur.execute('SELECT * FROM pg_stat_activity;')
    assert len(cur.fetchall()) == 1, 'there is always only one connection'
    cur.close()
