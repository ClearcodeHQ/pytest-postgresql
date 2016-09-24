# Copyright (C) 2016 by Clearcode <http://clearcode.cc>
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
# along with pytest-postgresql. If not, see <http://www.gnu.org/licenses/>.
"""Helpers for port-for package."""
from itertools import chain

import port_for


class InvalidPortsDefinition(ValueError):
    """Exception raised if ports definition is not a valid string."""

    def __init__(self, ports):
        """Constructor for InvalidPortsDefinition exception."""
        self.ports = ports

    def __str__(self):
        """String representation."""
        return (
            'Unknown format of ports: {0}.\n'
            'You should provide a ports range "[(4000,5000)]"'
            'or "(4000,5000)" or a comma-separated ports set'
            '"[{4000,5000,6000}]" or list of ints "[400,5000,6000,8000]"'
            'or all of them "[(20000, 30000), {48889, 50121}, 4000, 4004]"'
        ).format(self.ports)


def get_port(ports):
    """
    Retun a random available port.

    If there's only one port passed (e.g. 5000 or '5000') function
    does not check if port is available.
    it there's -1 passed as an argument, function returns None.
    When a range or list of ports is passed `port_for` external package
    is used in order to find a free port.

    :param str|int|tuple|set|list port:
        exact port (e.g. '8000', 8000)
        randomly selected port (None) - any random available port
        [(2000,3000)] or (2000,3000) - random available port from a given range
        [{4002,4003}] or {4002,4003} - random of 4002 or 4003 ports
        [(2000,3000), {4002,4003}] -random of given orange and set
    :returns: a random free port
    :raises: ValueError
    """
    if ports == -1:
        return None
    elif not ports:
        return port_for.select_random(None)

    try:
        return int(ports)
    except TypeError:
        pass

    ports_set = set()

    try:
        if not isinstance(ports, list):
            ports = [ports]
        ranges = port_for.utils.ranges_to_set(filter_by_type(ports, tuple))
        nums = set(filter_by_type(ports, int))
        sets = set(chain(*filter_by_type(ports, (set, frozenset))))
        ports_set = ports_set.union(ranges, sets, nums)
    except ValueError:
        raise InvalidPortsDefinition

    return port_for.select_random(ports_set)


def filter_by_type(lst, type_of):
    """Return a list of elements with given type."""
    return [e for e in lst if isinstance(e, type_of)]
