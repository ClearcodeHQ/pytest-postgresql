"""Test various executor behaviours."""

import sys
from typing import Any

import psycopg
import pytest
from packaging.version import parse
from port_for import get_port
from psycopg import Connection
from pytest import FixtureRequest

from pytest_postgresql.config import get_config
from pytest_postgresql.exceptions import PostgreSQLUnsupported
from pytest_postgresql.executor import PostgreSQLExecutor
from pytest_postgresql.factories import postgresql, postgresql_proc
from pytest_postgresql.retry import retry


def assert_executor_start_stop(executor):
    """Check that the executor is working."""
    with executor:
        assert executor.running()
        psycopg.connect(
            dbname=executor.user,
            user=executor.user,
            password=executor.password,
            host=executor.host,
            port=executor.port,
        )
        with pytest.raises(psycopg.OperationalError):
            psycopg.connect(
                dbname=executor.user,
                user=executor.user,
                password="bogus",
                host=executor.host,
                port=executor.port,
            )
    assert not executor.running()


class PatchedPostgreSQLExecutor(PostgreSQLExecutor):
    """PostgreSQLExecutor that always says it's 8.9 version."""

    @property
    def version(self) -> Any:
        """Overwrite version, to always return highest unsupported version."""
        return parse("8.9")


def test_unsupported_version(request: FixtureRequest) -> None:
    """Check that the error gets raised on unsupported postgres version."""
    config = get_config(request)
    port = get_port(config["port"])
    assert port is not None
    executor = PatchedPostgreSQLExecutor(
        executable=config["exec"],
        host=config["host"],
        port=port,
        datadir="/tmp/error",
        unixsocketdir=config["unixsocketdir"],
        logfile="/tmp/version.error.log",
        startparams=config["startparams"],
        dbname="random_name",
    )

    with pytest.raises(PostgreSQLUnsupported):
        executor.start()


@pytest.mark.skipif(
    sys.platform == "darwin", reason="The default pg_ctl path is for linux, not macos"
)
@pytest.mark.parametrize("locale", ("en_US.UTF-8", "de_DE.UTF-8"))
def test_executor_init_with_password(
    request: FixtureRequest,
    monkeypatch: pytest.MonkeyPatch,
    tmp_path_factory: pytest.TempPathFactory,
    locale: str,
) -> None:
    """Test whether the executor initializes properly."""
    config = get_config(request)
    monkeypatch.setenv("LC_ALL", locale)
    port = get_port(config["port"])
    assert port is not None
    tmpdir = tmp_path_factory.mktemp(f"pytest-postgresql-{request.node.name}")
    datadir = tmpdir / f"data-{port}"
    datadir.mkdir()
    logfile_path = tmpdir / f"postgresql.{port}.log"
    executor = PostgreSQLExecutor(
        executable=config["exec"],
        host=config["host"],
        port=port,
        datadir=str(datadir),
        unixsocketdir=config["unixsocketdir"],
        logfile=str(logfile_path),
        startparams=config["startparams"],
        password="somepassword",
        dbname="somedatabase",
    )
    assert_executor_start_stop(executor)


@pytest.mark.skipif(
    sys.platform == "darwin", reason="The default pg_ctl path is for linux, not macos"
)
def test_executor_init_bad_tmp_path(
    request: FixtureRequest,
    tmp_path_factory: pytest.TempPathFactory,
) -> None:
    r"""Test init when \ char is in tmp path."""
    config = get_config(request)
    port = get_port(config["port"])
    assert port is not None
    tmpdir = tmp_path_factory.mktemp(f"pytest-postgresql-{request.node.name}") / r"bad\path/"
    tmpdir.mkdir()
    datadir = tmpdir / f"data-{port}"
    datadir.mkdir()
    logfile_path = tmpdir / f"postgresql.{port}.log"
    executor = PostgreSQLExecutor(
        executable=config["exec"],
        host=config["host"],
        port=port,
        datadir=str(datadir),
        unixsocketdir=config["unixsocketdir"],
        logfile=str(logfile_path),
        startparams=config["startparams"],
        password="somepassword",
        dbname="somedatabase",
    )
    assert_executor_start_stop(executor)


postgres_with_password = postgresql_proc(password="hunter2")


def test_proc_with_password(
    postgres_with_password: PostgreSQLExecutor,
) -> None:
    """Check that password option to postgresql_proc factory is honored."""
    assert postgres_with_password.running() is True

    # no assertion necessary here; we just want to make sure it connects with
    # the password
    retry(
        lambda: psycopg.connect(
            dbname=postgres_with_password.user,
            user=postgres_with_password.user,
            password=postgres_with_password.password,
            host=postgres_with_password.host,
            port=postgres_with_password.port,
        ),
        possible_exception=psycopg.OperationalError,
    )

    with pytest.raises(psycopg.OperationalError):
        psycopg.connect(
            dbname=postgres_with_password.user,
            user=postgres_with_password.user,
            password="bogus",
            host=postgres_with_password.host,
            port=postgres_with_password.port,
        )


postgresql_max_conns_proc = postgresql_proc(postgres_options="-N 42")
postgres_max_conns = postgresql("postgresql_max_conns_proc")


def test_postgres_options(postgres_max_conns: Connection) -> None:
    """Check that max connections (-N 42) is honored."""
    cur = postgres_max_conns.cursor()
    cur.execute("SHOW max_connections")
    assert cur.fetchone() == ("42",)


postgres_isolation_level = postgresql(
    "postgresql_proc", isolation_level=psycopg.IsolationLevel.SERIALIZABLE
)


def test_custom_isolation_level(postgres_isolation_level: Connection) -> None:
    """Check that a client fixture with a custom isolation level works."""
    cur = postgres_isolation_level.cursor()
    cur.execute("SELECT 1")
    assert cur.fetchone() == (1,)
