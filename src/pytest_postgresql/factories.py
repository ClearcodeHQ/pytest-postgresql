# Copyright (C) 2013-2020 by Clearcode <http://clearcode.cc>
# and associates (see AUTHORS).

# This file is part of pytest-postgresql.

# pytest-dbfixtures is free software: you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# pytest-dbfixtures is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Lesser General Public License for more details.

# You should have received a copy of the GNU Lesser General Public License
# along with pytest-dbfixtures.  If not, see <http://www.gnu.org/licenses/>.
"""Fixture factories for postgresql fixtures."""

import os.path
import platform
import subprocess
from tempfile import gettempdir
from typing import List, Callable, Union, Iterable
from warnings import warn

import pytest
from _pytest.fixtures import FixtureRequest
from _pytest.tmpdir import TempdirFactory

from pytest_postgresql.compat import psycopg2, connection
from pytest_postgresql.executor_noop import NoopExecutor
from pytest_postgresql.janitor import DatabaseJanitor
from pytest_postgresql.executor import PostgreSQLExecutor
from pytest_postgresql.port import get_port


def get_config(request: FixtureRequest) -> dict:
    """Return a dictionary with config options."""
    config = {}
    options = [
        'exec', 'host', 'port', 'user', 'password', 'options', 'startparams',
        'logsprefix', 'unixsocketdir', 'dbname', 'load', 'postgres_options',
    ]
    for option in options:
        option_name = 'postgresql_' + option
        conf = request.config.getoption(option_name) or \
            request.config.getini(option_name)
        config[option] = conf
    return config


def init_postgresql_database(user, host, port, db_name, password=None):
    """
    Create database in postgresql.

    :param str user: postgresql username
    :param str host: postgresql host
    :param str port: postgresql port
    :param str db_name: database name
    :param str password: optional postgresql password
    """
    warn(
        'init_postgresql_database is deprecated, '
        'use DatabaseJanitor.init instead.',
        DeprecationWarning
    )
    DatabaseJanitor(user, host, port, db_name, 0.0, password).init()


def drop_postgresql_database(user, host, port, db_name, version, password=None):
    """
    Drop databse in postgresql.

    :param str user: postgresql username
    :param str host: postgresql host
    :param str port: postgresql port
    :param str db_name: database name
    :param packaging.version.Version version: postgresql version number
    :param str password: optional postgresql password
    """
    warn(
        'drop_postgresql_database is deprecated, '
        'use DatabaseJanitor.drop instead.',
        DeprecationWarning
    )
    DatabaseJanitor(user, host, port, db_name, version, password).drop()


def postgresql_proc(
        executable: str = None, host: str = None, port: Union[str, int, Iterable] = -1,
        user: str = None, password: str = None,
        options: str = '', startparams: str = None, unixsocketdir: str = None,
        logs_prefix: str = '', postgres_options: str = None,
) -> Callable[[FixtureRequest, TempdirFactory], PostgreSQLExecutor]:
    """
    Postgresql process factory.

    :param str executable: path to postgresql_ctl
    :param str host: hostname
    :param str|int|tuple|set|list port:
        exact port (e.g. '8000', 8000)
        randomly selected port (None) - any random available port
        -1 - command line or pytest.ini configured port
        [(2000,3000)] or (2000,3000) - random available port from a given range
        [{4002,4003}] or {4002,4003} - random of 4002 or 4003 ports
        [(2000,3000), {4002,4003}] - random of given range and set
    :param str user: postgresql username
    :param str options: Postgresql connection options
    :param str startparams: postgresql starting parameters
    :param str unixsocketdir: directory to create postgresql's unixsockets
    :param str logs_prefix: prefix for log filename
    :param str postgres_options: Postgres executable options for use by pg_ctl
    :rtype: func
    :returns: function which makes a postgresql process
    """

    @pytest.fixture(scope='session')
    def postgresql_proc_fixture(
            request: FixtureRequest, tmpdir_factory: TempdirFactory
    ) -> PostgreSQLExecutor:
        """
        Process fixture for PostgreSQL.

        :param FixtureRequest request: fixture request object
        :rtype: pytest_dbfixtures.executors.TCPExecutor
        :returns: tcp executor
        """
        config = get_config(request)
        postgresql_ctl = executable or config['exec']
        # check if that executable exists, as it's no on system PATH
        # only replace if executable isn't passed manually
        if not os.path.exists(postgresql_ctl) and executable is None:
            pg_bindir = subprocess.check_output(
                ['pg_config', '--bindir'], universal_newlines=True
            ).strip()
            postgresql_ctl = os.path.join(pg_bindir, 'pg_ctl')
        pg_port = get_port(port) or get_port(config['port'])
        datadir = os.path.join(
            gettempdir(), 'postgresqldata.{}'.format(pg_port))
        logfile_path = tmpdir_factory.mktemp("data").join(
            '{prefix}postgresql.{port}.log'.format(
                prefix=logs_prefix,
                port=pg_port
            )
        )

        if platform.system() == 'FreeBSD':
            with (datadir / 'pg_hba.conf').open(mode='a') as conf_file:
                conf_file.write('host all all 0.0.0.0/0 trust\n')

        postgresql_executor = PostgreSQLExecutor(
            executable=postgresql_ctl,
            host=host or config['host'],
            port=pg_port,
            user=user or config['user'],
            password=password or config['password'],
            options=options or config['options'],
            datadir=datadir,
            unixsocketdir=unixsocketdir or config['unixsocketdir'],
            logfile=logfile_path,
            startparams=startparams or config['startparams'],
            postgres_options=postgres_options or config['postgres_options']
        )
        # start server
        with postgresql_executor:
            postgresql_executor.wait_for_postgres()

            yield postgresql_executor

    return postgresql_proc_fixture


def postgresql_noproc(
        host: str = None, port: Union[str, int] = None, user: str = None, password: str = None,
        options: str = '',
) -> Callable[[FixtureRequest], NoopExecutor]:
    """
    Postgresql noprocess factory.

    :param host: hostname
    :param port: exact port (e.g. '8000', 8000)
    :param user: postgresql username
    :param password: postgresql password
    :param options: Postgresql connection options
    :returns: function which makes a postgresql process
    """

    @pytest.fixture(scope='session')
    def postgresql_noproc_fixture(request: FixtureRequest) -> NoopExecutor:
        """
        Noop Process fixture for PostgreSQL.

        :param FixtureRequest request: fixture request object
        :returns: tcp executor-like object
        """
        config = get_config(request)
        pg_host = host or config['host']
        pg_port = port or config['port'] or 5432
        pg_user = user or config['user']
        pg_password = password or config['password']
        pg_options = options or config['options']

        noop_exec = NoopExecutor(
            host=pg_host,
            port=pg_port,
            user=pg_user,
            password=pg_password,
            options=pg_options,
        )

        yield noop_exec

    return postgresql_noproc_fixture


def postgresql(
        process_fixture_name: str, db_name: str = None, load: List[str] = None,
        isolation_level: int = psycopg2.extensions.ISOLATION_LEVEL_AUTOCOMMIT,
) -> Callable[[FixtureRequest], connection]:
    """
    Return connection fixture factory for PostgreSQL.

    :param process_fixture_name: name of the process fixture
    :param db_name: database name
    :param load: SQL to automatically load into our test database
    :param isolation_level: optional postgresql isolation level
                            defaults to ISOLATION_LEVEL_AUTOCOMMIT
    :returns: function which makes a connection to postgresql
    """

    @pytest.fixture
    def postgresql_factory(request: FixtureRequest) -> connection:
        """
        Fixture factory for PostgreSQL.

        :param FixtureRequest request: fixture request object
        :returns: postgresql client
        """
        config = get_config(request)
        if not psycopg2:
            raise ImportError(
                'No module named psycopg2. Please install either '
                'psycopg2 or psycopg2-binary package for CPython '
                'or psycopg2cffi for Pypy.'
            )
        proc_fixture: Union[PostgreSQLExecutor, NoopExecutor] = request.getfixturevalue(
            process_fixture_name)

        pg_host = proc_fixture.host
        pg_port = proc_fixture.port
        pg_user = proc_fixture.user
        pg_password = proc_fixture.password
        pg_options = proc_fixture.options
        pg_db = db_name or config['dbname']
        pg_load = load or config['load']

        with DatabaseJanitor(
                pg_user, pg_host, pg_port, pg_db, proc_fixture.version,
                pg_password, isolation_level
        ):
            db_connection: connection = psycopg2.connect(
                dbname=pg_db,
                user=pg_user,
                password=pg_password,
                host=pg_host,
                port=pg_port,
                options=pg_options
            )
            if pg_load:
                for filename in pg_load:
                    with open(filename, 'r') as _fd:
                        with db_connection.cursor() as cur:
                            cur.execute(_fd.read())
            yield db_connection
            db_connection.close()

    return postgresql_factory


__all__ = ('postgresql', 'postgresql_proc')
