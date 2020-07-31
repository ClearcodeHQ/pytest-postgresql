"""Test various executor behaviours."""
import psycopg2
import pytest
from pkg_resources import parse_version

from pytest_postgresql.executor import PostgreSQLExecutor, PostgreSQLUnsupported
from pytest_postgresql.factories import postgresql_proc
from pytest_postgresql.factories import get_config
from pytest_postgresql.port import get_port


class PatchedPostgreSQLExecutor(PostgreSQLExecutor):
    """PostgreSQLExecutor that always says it's 8.9 version."""

    @property
    def version(self):
        """Overwrite version, to always return highes unsupported version."""
        return parse_version('8.9')


def test_unsupported_version(request):
    """Check that the error gets raised on unsupported postgres version."""
    config = get_config(request)
    executor = PatchedPostgreSQLExecutor(
        executable=config['exec'],
        host=config['host'],
        port=get_port(config['port']),
        datadir='/tmp/error',
        unixsocketdir=config['unixsocketdir'],
        logfile='/tmp/version.error.log',
        startparams=config['startparams'],

    )

    with pytest.raises(PostgreSQLUnsupported):
        executor.start()


postgres_with_password = postgresql_proc(password='hunter2')


def test_proc_with_password(
        postgres_with_password):  # pylint: disable=redefined-outer-name
    """Check that password option to postgresql_proc factory is honored."""
    assert postgres_with_password.running() is True

    # no assertion necessary here; we just want to make sure it connects with
    # the password
    psycopg2.connect(
        dbname=postgres_with_password.user,
        user=postgres_with_password.user,
        password=postgres_with_password.password,
        host=postgres_with_password.host,
        port=postgres_with_password.port)

    with pytest.raises(psycopg2.OperationalError):
        psycopg2.connect(
            dbname=postgres_with_password.user,
            user=postgres_with_password.user,
            password='bogus',
            host=postgres_with_password.host,
            port=postgres_with_password.port)
