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
"""Fixture factory for postgresql client."""
from typing import List, Optional, Callable, Union, Iterator

import pytest
from pytest import FixtureRequest

from pytest_postgresql.compat import connection, check_for_psycopg, psycopg
from pytest_postgresql.executor import PostgreSQLExecutor
from pytest_postgresql.executor_noop import NoopExecutor
from pytest_postgresql.janitor import DatabaseJanitor


def postgresql(
    process_fixture_name: str,
    dbname: Optional[str] = None,
    load: Optional[List[Union[Callable, str]]] = None,
    isolation_level: "Optional[psycopg.IsolationLevel]" = None,
) -> Callable[[FixtureRequest], Iterator[connection]]:
    """
    Return connection fixture factory for PostgreSQL.

    :param process_fixture_name: name of the process fixture
    :param dbname: database name
    :param load: SQL, function or function import paths to automatically load
                 into our test database
    :param isolation_level: optional postgresql isolation level
                            defaults to server's default
    :returns: function which makes a connection to postgresql
    """

    @pytest.fixture
    def postgresql_factory(request: FixtureRequest) -> Iterator[connection]:
        """
        Fixture factory for PostgreSQL.

        :param request: fixture request object
        :returns: postgresql client
        """
        check_for_psycopg()
        proc_fixture: Union[PostgreSQLExecutor, NoopExecutor] = request.getfixturevalue(
            process_fixture_name
        )

        pg_host = proc_fixture.host
        pg_port = proc_fixture.port
        pg_user = proc_fixture.user
        pg_password = proc_fixture.password
        pg_options = proc_fixture.options
        pg_db = dbname or proc_fixture.dbname
        pg_load = load or []

        with DatabaseJanitor(
            pg_user, pg_host, pg_port, pg_db, proc_fixture.version, pg_password, isolation_level
        ) as janitor:
            db_connection: connection = psycopg.connect(
                dbname=pg_db,
                user=pg_user,
                password=pg_password,
                host=pg_host,
                port=pg_port,
                options=pg_options,
            )
            for load_element in pg_load:
                janitor.load(load_element)
            yield db_connection
            db_connection.close()

    return postgresql_factory
