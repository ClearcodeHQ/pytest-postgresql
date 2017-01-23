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
import time
import shutil
import platform
import subprocess
from tempfile import gettempdir

import pytest
import psycopg2

from pytest_postgresql.executor import PostgreSQLExecutor
from pytest_postgresql.port import get_port


def get_config(request):
    """Return a dictionary with config options."""
    config = {}
    options = [
        'exec', 'host', 'port', 'user', 'startparams', 'logsdir',
        'logsprefix', 'unixsocketdir'
    ]
    for option in options:
        option_name = 'postgresql_' + option
        conf = request.config.getoption(option_name) or \
            request.config.getini(option_name)
        config[option] = conf
    return config


START_INFO = 'database system is ready to accept connections'


def wait_for_postgres(logfile, awaited_msg):
    """
    Wait for postgresql being started.

    :param str logfile: logfile path
    :param str awaited_msg: awaited message
    """
    # wait until logfile is created
    while not os.path.isfile(logfile):
        time.sleep(1)

    # wait for expected message.
    while 1:
        with open(logfile, 'r') as content_file:
            content = content_file.read()
            if awaited_msg in content:
                break
        time.sleep(1)


def remove_postgresql_directory(datadir):
    """
    Remove directory created for postgresql run.

    :param str datadir: datadir path
    """
    if os.path.isdir(datadir):
        shutil.rmtree(datadir)


def init_postgresql_directory(postgresql_ctl, user, datadir):
    """
    Initialize postgresql data directory.

    See `Initialize postgresql data directory
        <www.postgresql.org/docs/9.5/static/app-initdb.html>`_

    :param str postgresql_ctl: ctl path
    :param str user: postgresql username
    :param str datadir: datadir path

    """
    # remove old one if exists first.
    remove_postgresql_directory(datadir)
    init_directory = (
        postgresql_ctl, 'initdb',
        '-o "--auth=trust --username=%s"' % user,
        '-D %s' % datadir,
    )
    subprocess.check_output(' '.join(init_directory), shell=True)


def init_postgresql_database(user, host, port, db):
    """
    Create database in postgresql.

    :param str user: postgresql username
    :param str host: postgresql host
    :param str port: postgresql port
    :param str db: database name
    """
    conn = psycopg2.connect(user=user, host=host, port=port)
    conn.set_isolation_level(psycopg2.extensions.ISOLATION_LEVEL_AUTOCOMMIT)
    cur = conn.cursor()
    cur.execute('CREATE DATABASE {0};'.format(db))
    cur.close()
    conn.close()


def drop_postgresql_database(user, host, port, db, version):
    """
    Drop databse in postgresql.

    :param str user: postgresql username
    :param str host: postgresql host
    :param str port: postgresql port
    :param str db: database name
    :param str version: postgresql version number
    """
    conn = psycopg2.connect(user=user, host=host, port=port)
    conn.set_isolation_level(psycopg2.extensions.ISOLATION_LEVEL_AUTOCOMMIT)
    cur = conn.cursor()
    # We cannot drop the database while there are connections to it, so we
    # terminate all connections first while not allowing new connections.
    if float(version) >= 9.2:
        pid_column = 'pid'
    else:
        pid_column = 'procpid'
    cur.execute(
        'UPDATE pg_database SET datallowconn=false WHERE datname = %s;',
        (db,))
    cur.execute(
        'SELECT pg_terminate_backend(pg_stat_activity.{0})'
        'FROM pg_stat_activity WHERE pg_stat_activity.datname = %s;'.format(
            pid_column),
        (db,))
    cur.execute('DROP DATABASE IF EXISTS {0};'.format(db))
    cur.close()
    conn.close()


def postgresql_proc(
        executable=None, host=None, port=-1, user=None,
        startparams=None, unixsocketdir=None, logsdir=None, logs_prefix='',
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
    :param str startparams: postgresql starting parameters
    :param str unixsocketdir: directory to create postgresql's unixsockets
    :param str logsdir: location for logs
    :param str logs_prefix: prefix for log filename
    :rtype: func
    :returns: function which makes a postgresql process
    """
    @pytest.fixture(scope='session')
    def postgresql_proc_fixture(request):
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
            gettempdir(), 'postgresqldata.{0}'.format(pg_port))
        pg_user = user or config['user']
        pg_unixsocketdir = unixsocketdir or config['unixsocketdir']
        pg_startparams = startparams or config['startparams']
        pg_logsdir = logsdir or config['logsdir']
        logfile_path = os.path.join(
            pg_logsdir, '{prefix}postgresql.{port}.log'.format(
                prefix=logs_prefix,
                port=pg_port
            ))

        init_postgresql_directory(
            postgresql_ctl, pg_user, datadir
        )

        if 'FreeBSD' == platform.system():
            with (datadir / 'pg_hba.conf').open(mode='a') as f:
                f.write('host all all 0.0.0.0/0 trust\n')

        postgresql_executor = PostgreSQLExecutor(
            executable=postgresql_ctl,
            host=pg_host,
            port=pg_port,
            user=pg_user,
            datadir=datadir,
            unixsocketdir=pg_unixsocketdir,
            logfile=logfile_path,
            startparams=pg_startparams,
        )

        def stop_server_and_remove_directory():
            postgresql_executor.stop()
            remove_postgresql_directory(datadir)

        request.addfinalizer(stop_server_and_remove_directory)

        # start server
        postgresql_executor.start()
        if '-w' in pg_startparams:
            wait_for_postgres(logfile_path, START_INFO)

        return postgresql_executor

    return postgresql_proc_fixture


def postgresql(process_fixture_name, db='tests'):
    """
    Connection fixture factory for PostgreSQL.

    :param str process_fixture_name: name of the process fixture
    :param str db: database name
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
        proc_fixture = request.getfixturevalue(process_fixture_name)

        # _, config = try_import('psycopg2', request)
        pg_host = proc_fixture.host
        pg_port = proc_fixture.port
        pg_user = proc_fixture.user
        pg_db = db

        init_postgresql_database(
            pg_user, pg_host, pg_port, pg_db
        )
        connection = psycopg2.connect(
            dbname=pg_db,
            user=pg_user,
            host=pg_host,
            port=pg_port
        )

        def drop_database():
            connection.close()
            drop_postgresql_database(
                pg_user, pg_host, pg_port, pg_db,
                proc_fixture.version
            )

        request.addfinalizer(drop_database)

        return connection

    return postgresql_factory


__all__ = ('postgresql', 'postgresql_proc')
