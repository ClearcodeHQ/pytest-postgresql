# Copyright (C) 2013-2021 by Clearcode <http://clearcode.cc>
# and associates (see AUTHORS).

# This file is part of pytest-postgresql.

# pytest-postgresql is free software: you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# pytest-postgresql is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Lesser General Public License for more details.

# You should have received a copy of the GNU Lesser General Public License
# along with pytest-postgresql.  If not, see <http://www.gnu.org/licenses/>.
"""Fixture factory for existing postgresql server."""
import os
from pathlib import Path
from typing import Callable, Iterator, List, Optional, Union

import pytest
from pytest import FixtureRequest

from pytest_postgresql.config import get_config
from pytest_postgresql.executor_noop import NoopExecutor
from pytest_postgresql.janitor import DatabaseJanitor


def xdistify_dbname(dbname: str) -> str:
    """Modify the database name depending on the presence and usage of xdist."""
    xdist_worker = os.getenv("PYTEST_XDIST_WORKER")
    if xdist_worker:
        return f"{dbname}{xdist_worker}"
    return dbname


def postgresql_noproc(
    host: Optional[str] = None,
    port: Union[str, int, None] = None,
    user: Optional[str] = None,
    password: Optional[str] = None,
    dbname: Optional[str] = None,
    options: str = "",
    load: Optional[List[Union[Callable, str, Path]]] = None,
) -> Callable[[FixtureRequest], Iterator[NoopExecutor]]:
    """Postgresql noprocess factory.

    :param host: hostname
    :param port: exact port (e.g. '8000', 8000)
    :param user: postgresql username
    :param password: postgresql password
    :param dbname: postgresql database name
    :param options: Postgresql connection options
    :param load: List of functions used to initialize database's template.
    :returns: function which makes a postgresql process
    """

    @pytest.fixture(scope="session")
    def postgresql_noproc_fixture(request: FixtureRequest) -> Iterator[NoopExecutor]:
        """Noop Process fixture for PostgreSQL.

        :param request: fixture request object
        :returns: tcp executor-like object
        """
        config = get_config(request)
        pg_host = host or config["host"]
        pg_port = port or config["port"] or 5432
        pg_user = user or config["user"]
        pg_password = password or config["password"]
        pg_dbname = xdistify_dbname(dbname or config["dbname"])
        pg_options = options or config["options"]
        pg_load = load or config["load"]

        noop_exec = NoopExecutor(
            host=pg_host,
            port=pg_port,
            user=pg_user,
            password=pg_password,
            dbname=pg_dbname,
            options=pg_options,
        )
        with DatabaseJanitor(
            user=noop_exec.user,
            host=noop_exec.host,
            port=noop_exec.port,
            template_dbname=noop_exec.template_dbname,
            version=noop_exec.version,
            password=noop_exec.password,
        ) as janitor:
            for load_element in pg_load:
                janitor.load(load_element)
            yield noop_exec

    return postgresql_noproc_fixture
