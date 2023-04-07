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
"""Fixture factories for postgresql fixtures."""

from pytest_postgresql.factories.process import postgresql_proc
from pytest_postgresql.factories.noprocess import postgresql_noproc
from pytest_postgresql.factories.client import postgresql

__all__ = ("postgresql_proc", "postgresql_noproc", "postgresql")
