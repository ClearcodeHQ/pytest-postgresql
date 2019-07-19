"""Test various executor behaviours."""
import pytest
from pkg_resources import parse_version

from pytest_postgresql.executor import PostgreSQLExecutor, PostgreSQLUnsupported
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
