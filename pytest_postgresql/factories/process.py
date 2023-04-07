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
from typing import Union, Callable, List, Iterator, Optional, Tuple, Set
from warnings import warn

import pytest
from pytest import FixtureRequest, TempPathFactory
from port_for import get_port

from pytest_postgresql.config import get_config
from pytest_postgresql.executor import PostgreSQLExecutor
from pytest_postgresql.janitor import DatabaseJanitor


def postgresql_proc(
    executable: Optional[str] = None,
    host: Optional[str] = None,
    port: Union[
        None,
        str,
        int,
        Tuple[int, int],
        Set[int],
        List[str],
        List[int],
        List[Tuple[int, int]],
        List[Set[int]],
        List[Union[Set[int], Tuple[int, int]]],
        List[Union[str, int, Tuple[int, int], Set[int]]],
    ] = -1,
    user: Optional[str] = None,
    password: Optional[str] = None,
    dbname: Optional[str] = None,
    options: str = "",
    startparams: Optional[str] = None,
    unixsocketdir: Optional[str] = None,
    logs_prefix: str = "",
    postgres_options: Optional[str] = None,
    load: Optional[List[Union[Callable, str]]] = None,
) -> Callable[[FixtureRequest, TempPathFactory], Iterator[PostgreSQLExecutor]]:
    """
    Postgresql process factory.

    :param executable: path to postgresql_ctl
    :param host: hostname
    :param port:
        exact port (e.g. '8000', 8000)
        randomly selected port (None) - any random available port
        -1 - command line or pytest.ini configured port
        [(2000,3000)] or (2000,3000) - random available port from a given range
        [{4002,4003}] or {4002,4003} - random of 4002 or 4003 ports
        [(2000,3000), {4002,4003}] - random of given range and set
    :param user: postgresql username
    :param password: postgresql password
    :param dbname: postgresql database name
    :param options: Postgresql connection options
    :param startparams: postgresql starting parameters
    :param unixsocketdir: directory to create postgresql's unixsockets
    :param logs_prefix: prefix for log filename
    :param postgres_options: Postgres executable options for use by pg_ctl
    :param load: List of functions used to initialize database's template.
    :returns: function which makes a postgresql process
    """

    @pytest.fixture(scope="session")
    def postgresql_proc_fixture(
        request: FixtureRequest, tmp_path_factory: TempPathFactory
    ) -> Iterator[PostgreSQLExecutor]:
        """
        Process fixture for PostgreSQL.

        :param request: fixture request object
        :param tmp_path_factory: temporary path object (fixture)
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

        tmpdir = tmp_path_factory.mktemp(f"pytest-postgresql-{request.fixturename}")

        if logfile_prefix:
            warn(
                f"logfile_prefix and logsprefix config option is deprecated, "
                f"and will be dropped in future releases. All fixture related "
                f"data resides within {tmpdir}",
                DeprecationWarning,
            )

        pg_port = get_port(port) or get_port(config["port"])
        assert pg_port is not None
        datadir = tmpdir / f"data-{pg_port}"
        datadir.mkdir()
        logfile_path = tmpdir / f"{logfile_prefix}postgresql.{pg_port}.log"

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
            datadir=str(datadir),
            unixsocketdir=unixsocketdir or config["unixsocketdir"],
            logfile=str(logfile_path),
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
