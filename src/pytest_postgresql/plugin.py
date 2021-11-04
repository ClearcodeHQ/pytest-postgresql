# Copyright (C) 2016 by Clearcode <http://clearcode.cc>
# and associates (see AUTHORS).

# This file is part of pytest-postgresql.

# pytest-dbfixtures is free software: you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# pytest-postgresql is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Lesser General Public License for more details.

# You should have received a copy of the GNU Lesser General Public License
# along with pytest-postgresql.  If not, see <http://www.gnu.org/licenses/>.
"""Plugin module of pytest-postgresql."""
from tempfile import gettempdir

from pytest_postgresql import factories
from _pytest.config.argparsing import Parser


_help_executable = "Path to PostgreSQL executable"
_help_host = "Host at which PostgreSQL will accept connections"
_help_port = "Port at which PostgreSQL will accept connections"
_help_user = "PostgreSQL username"
_help_password = "PostgreSQL password"
_help_options = "PostgreSQL connection options"
_help_startparams = "Starting parameters for the PostgreSQL"
_help_logsprefix = "Prefix for the log files"
_help_unixsocketdir = "Location of the socket directory"
_help_dbname = "Default database name"
_help_load = "Dotted-style or entrypoint-style path to callable or path to SQL File"
_help_postgres_options = "Postgres executable extra parameters. Passed via the -o option to pg_ctl"


def pytest_addoption(parser: Parser) -> None:
    """Configure options for pytest-postgresql."""
    parser.addini(
        name="postgresql_exec", help=_help_executable, default="/usr/lib/postgresql/13/bin/pg_ctl"
    )

    parser.addini(name="postgresql_host", help=_help_host, default="127.0.0.1")

    parser.addini(
        name="postgresql_port",
        help=_help_port,
        default=None,
    )

    parser.addini(name="postgresql_user", help=_help_user, default="postgres")

    parser.addini(name="postgresql_password", help=_help_password, default=None)

    parser.addini(name="postgresql_options", help=_help_options, default="")

    parser.addini(name="postgresql_startparams", help=_help_startparams, default="-w")

    parser.addini(name="postgresql_logsprefix", help=_help_logsprefix, default="")

    parser.addini(name="postgresql_unixsocketdir", help=_help_unixsocketdir, default=gettempdir())

    parser.addini(name="postgresql_dbname", help=_help_dbname, default="tests")

    parser.addini(name="postgresql_load", type="pathlist", help=_help_load, default=None)
    parser.addini(name="postgresql_postgres_options", help=_help_postgres_options, default="")

    parser.addoption(
        "--postgresql-exec",
        action="store",
        metavar="path",
        dest="postgresql_exec",
        help=_help_executable,
    )

    parser.addoption(
        "--postgresql-host",
        action="store",
        dest="postgresql_host",
        help=_help_host,
    )

    parser.addoption("--postgresql-port", action="store", dest="postgresql_port", help=_help_port)

    parser.addoption("--postgresql-user", action="store", dest="postgresql_user", help=_help_user)

    parser.addoption(
        "--postgresql-password", action="store", dest="postgresql_password", help=_help_password
    )

    parser.addoption(
        "--postgresql-options", action="store", dest="postgresql_options", help=_help_options
    )

    parser.addoption(
        "--postgresql-startparams",
        action="store",
        dest="postgresql_startparams",
        help=_help_startparams,
    )

    parser.addoption(
        "--postgresql-logsprefix",
        action="store",
        dest="postgresql_logsprefix",
        help=_help_logsprefix,
    )

    parser.addoption(
        "--postgresql-unixsocketdir",
        action="store",
        dest="postgresql_unixsocketdir",
        help=_help_unixsocketdir,
    )

    parser.addoption(
        "--postgresql-dbname", action="store", dest="postgresql_dbname", help=_help_dbname
    )

    parser.addoption("--postgresql-load", action="append", dest="postgresql_load", help=_help_load)

    parser.addoption(
        "--postgresql-postgres-options",
        action="store",
        dest="postgresql_postgres_options",
        help=_help_postgres_options,
    )


postgresql_proc = factories.postgresql_proc()
postgresql_noproc = factories.postgresql_noproc()
postgresql = factories.postgresql("postgresql_proc")
