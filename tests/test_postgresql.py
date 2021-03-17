"""All tests for pytest-postgresql."""
import decimal
from datetime import datetime, timedelta
from time import sleep

import psycopg2
import pytest

from tests.conftest import POSTGRESQL_VERSION

MAKE_Q = "CREATE TABLE test (id serial PRIMARY KEY, num integer, data varchar);"
SELECT_Q = "SELECT * FROM test;"


def test_postgresql_proc(postgresql_proc_version):
    """Test different postgresql versions."""
    assert postgresql_proc_version.running() is True


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


def wait_for(func, timeout=60):
    """Check for function to finish."""
    time: datetime = datetime.utcnow()
    timeout_diff: timedelta = timedelta(seconds=timeout)
    i = 0
    while True:
        i += 1
        try:
            func()
            return
        except AssertionError as e:
            if time + timeout_diff < datetime.utcnow():
                raise AssertionError("Faile after {i} attempts".format(i=i)) from e
            sleep(1)
            pass


@pytest.mark.skipif(
    decimal.Decimal(POSTGRESQL_VERSION) < 10,
    reason="Test query not supported in those postgresql versions, and soon will not be supported."
)
@pytest.mark.parametrize('_', range(2))
def test_postgres_terminate_connection(
        postgresql_version, _):
    """
    Test that connections are terminated between tests.

    And check that only one exists at a time.
    """

    with postgresql_version.cursor() as cur:
        def check_if_one_connection():
            cur.execute(
                'SELECT * FROM pg_stat_activity '
                'WHERE backend_type = \'client backend\';'
            )
            existing_connections = cur.fetchall()
            assert len(existing_connections) == 1, \
                'there is always only one connection, {}'.format(existing_connections)
        wait_for(check_if_one_connection, timeout=120)
