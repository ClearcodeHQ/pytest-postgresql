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
from pkg_resources import parse_version

from pytest_postgresql.janitor import psycopg2


class NoopExecutor:  # pylint: disable=too-few-public-methods
    """
    Nooperator executor.

    This executor actually does nothing more than provide connection details
    for existing PostgreSQL server. I.E. one already started either on machine
    or with the use of containerisation like kubernetes or docker compose.
    """

    def __init__(self, host, port, user, options, password=None):
        """
        Initialize nooperator executor mock.

        :param str host: Postgresql hostname
        :param str|int port: Postrgesql port
        :param str user: Postgresql username
        :param str user: Postgresql password
        :param str options: Additional connection options
        """
        self.host = host
        self.port = int(port)
        self.user = user
        self.options = options
        self.password = password
        self._version = None

    @property
    def version(self):
        """Get postgresql's version."""
        if not self._version:
            with psycopg2.connect(
                    dbname='postgres',
                    user=self.user,
                    host=self.host,
                    port=self.port,
                    password=self.password,
                    options=self.options
            ) as connection:
                version = str(connection.server_version)
                # Pad the version for releases before 10
                # if not we get 90524 instead of 090524
                if len(version) < 6:
                    version = '0' + version
                self._version = parse_version(
                    '.'.join([
                        version[i: i+2] for i in range(0, len(version), 2)
                        if int(version[i: i+2])
                        ][:2])
                )
        return self._version
