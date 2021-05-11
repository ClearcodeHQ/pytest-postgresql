# Copyright (C) 2013-2021 by Clearcode <http://clearcode.cc>
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
"""Fixture factory for postgresql process."""
import os.path
import platform
import subprocess
from _warnings import warn
from typing import Union, Iterable, Callable, List

import pytest
from _pytest.fixtures import FixtureRequest
from _pytest.tmpdir import TempdirFactory

from pytest_postgresql.config import get_config
from pytest_postgresql.executor import PostgreSQLExecutor
from pytest_postgresql.janitor import DatabaseJanitor
from pytest_postgresql.port import get_port


def postgresql_proc(
    executable: str = None,
    host: str = None,
    port: Union[str, int, Iterable] = -1,
    user: str = None,
    password: str = None,
    dbname: str = None,
    options: str = "",
    startparams: str = None,
    unixsocketdir: str = None,
    logs_prefix: str = "",
    postgres_options: str = None,
    load: List[Union[Callable, str]] = None,
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
    :param password: postgresql password
    :param dbname: postgresql database name
    :param str options: Postgresql connection options
    :param str startparams: postgresql starting parameters
    :param str unixsocketdir: directory to create postgresql's unixsockets
    :param str logs_prefix: prefix for log filename
    :param str postgres_options: Postgres executable options for use by pg_ctl
    :param load: List of functions used to initialize database's template.
    :rtype: func
    :returns: function which makes a postgresql process
    """

    @pytest.fixture(scope="session")
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
        postgresql_ctl = executable or config["exec"]
        logfile_prefix = logs_prefix or config["logsprefix"]
        pg_dbname = dbname or config["dbname"]
        pg_load = load or config["load"]

        # check if that executable exists, as it's no on system PATH
        # only replace if executable isn't passed manually
        if not os.path.exists(postgresql_ctl) and executable is None:
            pg_bindir = subprocess.check_output(
                ["pg_config", "--bindir"], universal_newlines=True
            ).strip()
            postgresql_ctl = os.path.join(pg_bindir, "pg_ctl")

        tmpdir = tmpdir_factory.mktemp(f"pytest-postgresql-{request.fixturename}")

        if logfile_prefix:
            warn(
                f"logfile_prefix and logsprefix config option is deprecated, "
                f"and will be dropped in future releases. All fixture related "
                f"data resides within {tmpdir}",
                DeprecationWarning,
            )

        pg_port = get_port(port) or get_port(config["port"])
        datadir = tmpdir.mkdir(f"data-{pg_port}")
        logfile_path = tmpdir.join(f"{logfile_prefix}postgresql.{pg_port}.log")

        if platform.system() == "FreeBSD":
            with (datadir / "pg_hba.conf").open(mode="a") as conf_file:
                conf_file.write("host all all 0.0.0.0/0 trust\n")

        postgresql_executor = PostgreSQLExecutor(
            executable=postgresql_ctl,
            host=host or config["host"],
            port=pg_port,
            user=user or config["user"],
            password=password or config["password"],
            dbname=pg_dbname,
            options=options or config["options"],
            datadir=datadir,
            unixsocketdir=unixsocketdir or config["unixsocketdir"],
            logfile=logfile_path,
            startparams=startparams or config["startparams"],
            postgres_options=postgres_options or config["postgres_options"],
        )
        # start server
        with postgresql_executor:
            postgresql_executor.wait_for_postgres()
            template_dbname = f"{postgresql_executor.dbname}_tmpl"
            with DatabaseJanitor(
                user=postgresql_executor.user,
                host=postgresql_executor.host,
                port=postgresql_executor.port,
                dbname=template_dbname,
                version=postgresql_executor.version,
                password=postgresql_executor.password,
            ) as janitor:
                for load_element in pg_load:
                    janitor.load(load_element)
                yield postgresql_executor

    return postgresql_proc_fixture
