# Copyright (C) 2020 by Clearcode <http://clearcode.cc>
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
"""PostgreSQL Noop executor providing connection details for postgres client."""
from typing import Union, Optional, Any

from pkg_resources import parse_version

from pytest_postgresql.compat import check_for_psycopg2, psycopg2


class NoopExecutor:  # pylint: disable=too-few-public-methods
    """
    Nooperator executor.

    This executor actually does nothing more than provide connection details
    for existing PostgreSQL server. I.E. one already started either on machine
    or with the use of containerisation like kubernetes or docker compose.
    """

    def __init__(
        self,
        host: str,
        port: Union[str, int],
        user: str,
        options: str,
        password: Optional[str] = None,
        dbname: Optional[str] = None,
    ):
        """
        Initialize nooperator executor mock.

        :param host: Postgresql hostname
        :param port: Postgresql port
        :param user: Postgresql username
        :param options: Additional connection options
        :param password: postgresql password
        :param dbname: postgresql database name
        """
        self.host = host
        self.port = int(port)
        self.user = user
        self.options = options
        self.password = password
        self.dbname = dbname
        self._version: Any = None

    @property
    def version(self) -> Any:
        """Get postgresql's version."""
        if not self._version:
            check_for_psycopg2()
            # could be called before self.dbname will be created.
            # Use default postgres database
            with psycopg2.connect(
                dbname="postgres",
                user=self.user,
                host=self.host,
                port=self.port,
                password=self.password,
                options=self.options,
            ) as connection:
                version = str(connection.server_version)
                # Pad the version for releases before 10
                # if not we get 90524 instead of 090524
                if len(version) < 6:
                    version = "0" + version
                version_parts = []

                # extract version parts to construct a two-part version
                for i in range(0, len(version), 2):
                    j = i + 2
                    part = version[i:j]
                    if not int(part):
                        continue
                    version_parts.append(part)
                self._version = parse_version(".".join(version_parts[:2]))
        return self._version
