# Copyright (C) 2013-2016 by Clearcode <http://clearcode.cc>
# and associates (see AUTHORS).

# This file is part of pytest-dbfixtures.

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
from warnings import warn

import pytest
from pkg_resources import parse_version

from pytest_postgresql.janitor import DatabaseJanitor, psycopg2
from pytest_postgresql.executor import PostgreSQLExecutor
from pytest_postgresql.port import get_port


class NoopExecutor:  # pylint: disable=too-few-public-methods
    """Nooperator executor."""

    def __init__(self, host, port, user, options):
        """
        Initialize nooperator executor mock.

        :param str host: Postgresql hostname
        :param str|int port: Postrgesql port
        :param str user: Postgresql username
        :param str options: Additional connection options
        """
        self.host = host
        self.port = int(port)
        self.user = user
        self.options = options
        self._version = None

    @property
    def version(self):
        """Get postgresql's version."""
        if self._version:
            return self._version
        try:
            connection = psycopg2.connect(
                dbname='postgres',
                user=self.user,
                host=self.host,
                port=self.port,
                options=self.options
            )
            version = str(connection.server_version)
            self._version = parse_version(
                '.'.join([
                    version[i: i+2] for i in range(0, len(version), 2)
                    if int(version[i: i+2])
                ])
            )
            return self._version
        finally:
            connection.close()


def get_config(request):
    """Return a dictionary with config options."""
    config = {}
    options = [
        'exec', 'host', 'port', 'user', 'options', 'startparams',
        'logsprefix', 'unixsocketdir', 'dbname'
    ]
    for option in options:
        option_name = 'postgresql_' + option
        conf = request.config.getoption(option_name) or \
            request.config.getini(option_name)
        config[option] = conf
    return config


def init_postgresql_database(user, host, port, db_name):
    """
    Create database in postgresql.

    :param str user: postgresql username
    :param str host: postgresql host
    :param str port: postgresql port
    :param str db_name: database name
    """
    warn(
        'init_postgresql_database is deprecated, '
        'use DatabaseJanitor.init istead.',
        DeprecationWarning
    )
    DatabaseJanitor(user, host, port, db_name, 0.0).init()


def drop_postgresql_database(user, host, port, db_name, version):
    """
    Drop databse in postgresql.

    :param str user: postgresql username
    :param str host: postgresql host
    :param str port: postgresql port
    :param str db_name: database name
    :param packaging.version.Version version: postgresql version number
    """
    warn(
        'drop_postgresql_database is deprecated, '
        'use DatabaseJanitor.drop istead.',
        DeprecationWarning
    )
    DatabaseJanitor(user, host, port, db_name, version).init()


def postgresql_proc(
        executable=None, host=None, port=-1, user=None, options='',
        startparams=None, unixsocketdir=None, logs_prefix='',
):
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
    :rtype: func
    :returns: function which makes a postgresql process
    """
    @pytest.fixture(scope='session')
    def postgresql_proc_fixture(request, tmpdir_factory):
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

        pg_host = host or config['host']
        pg_port = get_port(port) or get_port(config['port'])
        datadir = os.path.join(
            gettempdir(), 'postgresqldata.{}'.format(pg_port))
        pg_user = user or config['user']
        pg_options = options or config['options']
        pg_unixsocketdir = unixsocketdir or config['unixsocketdir']
        pg_startparams = startparams or config['startparams']
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
            host=pg_host,
            port=pg_port,
            user=pg_user,
            options=pg_options,
            datadir=datadir,
            unixsocketdir=pg_unixsocketdir,
            logfile=logfile_path,
            startparams=pg_startparams,
        )
        # start server
        with postgresql_executor:
            postgresql_executor.wait_for_postgres()

            yield postgresql_executor

    return postgresql_proc_fixture


def postgresql_noproc(host=None, port=None, user=None, options=''):
    """
    Postgresql noprocess factory.

    :param str host: hostname
    :param str|int port: exact port (e.g. '8000', 8000)
    :param str user: postgresql username
    :param str options: Postgresql connection options
    :rtype: func
    :returns: function which makes a postgresql process
    """
    @pytest.fixture(scope='session')
    def postgresql_noproc_fixture(request):
        """
        Noop Process fixture for PostgreSQL.

        :param FixtureRequest request: fixture request object
        :rtype: pytest_dbfixtures.executors.TCPExecutor
        :returns: tcp executor-like object
        """
        config = get_config(request)
        pg_host = host or config['host']
        pg_port = port or config['port'] or 5432
        pg_user = user or config['user']
        pg_options = options or config['options']

        noop_exec = NoopExecutor(
            host=pg_host,
            port=pg_port,
            user=pg_user,
            options=pg_options,
        )

        yield noop_exec

    return postgresql_noproc_fixture


def postgresql(process_fixture_name, db_name=None):
    """
    Return connection fixture factory for PostgreSQL.

    :param str process_fixture_name: name of the process fixture
    :param str db_name: database name
    :rtype: func
    :returns: function which makes a connection to postgresql
    """
    @pytest.fixture
    def postgresql_factory(request):
        """
        Fixture factory for PostgreSQL.

        :param FixtureRequest request: fixture request object
        :rtype: psycopg2.connection
        :returns: postgresql client
        """
        config = get_config(request)
        if not psycopg2:
            raise ImportError(
                'No module named psycopg2. Please install either '
                'psycopg2 or psycopg2-binary package for CPython '
                'or psycopg2cffi for Pypy.'
            )
        proc_fixture = request.getfixturevalue(process_fixture_name)

        # _, config = try_import('psycopg2', request)
        pg_host = proc_fixture.host
        pg_port = proc_fixture.port
        pg_user = proc_fixture.user
        pg_options = proc_fixture.options
        pg_db = db_name or config['dbname']

        with DatabaseJanitor(
                pg_user, pg_host, pg_port, pg_db, proc_fixture.version
        ):
            connection = psycopg2.connect(
                dbname=pg_db,
                user=pg_user,
                host=pg_host,
                port=pg_port,
                options=pg_options
            )
            yield connection
            connection.close()

    return postgresql_factory


__all__ = ('postgresql', 'postgresql_proc')
