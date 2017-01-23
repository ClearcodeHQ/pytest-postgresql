# Copyright (C) 2013 by Clearcode <http://clearcode.cc>
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
"""PostgreSQL executor crafter around pg_ctl."""

import os.path
import re
import subprocess

from mirakuru import TCPExecutor


class PostgreSQLExecutor(TCPExecutor):
    """
    PostgreSQL executor running on pg_ctl.

    Based over an `pg_ctl program
    <http://www.postgresql.org/docs/9.1/static/app-pg-ctl.html>`_
    """

    BASE_PROC_START_COMMAND = """{executable} start -D {datadir}
    -o "-F -p {port} -c log_destination='stderr' -c %s='{unixsocketdir}'"
    -l {logfile} {startparams}"""

    def __init__(self, executable, host, port,
                 datadir, unixsocketdir, logfile, startparams,
                 shell=False, timeout=60, sleep=0.1, user='postgres'):
        """
        Initialize PostgreSQLExecutor executor.

        :param str executable: pg_ctl location
        :param str host: host under which process is accessible
        :param int port: port under which process is accessible
        :param str datadir: path to postgresql datadir
        :param str unixsocketdir: path to socket directory
        :param str logfile: path to logfile for postgresql
        :param str startparams: additional start parameters
        :param bool shell: see `subprocess.Popen`
        :param int timeout: time to wait for process to start or stop.
            if None, wait indefinitely.
        :param float sleep: how often to check for start/stop condition
        :param str user: [default] postgresql's username used to manage
            and access PostgreSQL
        """
        self.executable = executable
        self.user = user
        self.version = self.version()
        self.datadir = datadir
        self.unixsocketdir = unixsocketdir
        command = self.proc_start_command().format(
            executable=self.executable,
            datadir=self.datadir,
            port=port,
            unixsocketdir=self.unixsocketdir,
            logfile=logfile,
            startparams=startparams,
        )
        super(PostgreSQLExecutor, self).__init__(
            command, host, port, shell=shell, timeout=timeout, sleep=sleep)

    def proc_start_command(self):
        """Based on postgres version return proper start command."""
        if float(self.version) > 9.2:
            unix_socket_dir_arg_name = 'unix_socket_directories'
        else:
            unix_socket_dir_arg_name = 'unix_socket_directory'
        return self.BASE_PROC_START_COMMAND % unix_socket_dir_arg_name

    def version(self):
        """Detect postgresql version."""
        version_string = subprocess.check_output(
            [self.executable, '--version']).decode('utf-8')
        matches = re.search('.* (?P<version>\d\.\d)', version_string)
        return matches.groupdict()['version']

    def running(self):
        """Check if server is still running."""
        if not os.path.exists(self.datadir):
            return False

        output = subprocess.check_output(
            '{pg_ctl} status -D {datadir}'.format(
                pg_ctl=self.executable,
                datadir=self.datadir
            ),
            shell=True
        ).decode('utf-8')
        return "pg_ctl: server is running" in output

    def stop(self):
        """Issue a stop request to executable."""
        subprocess.check_output(
            '{pg_ctl} stop -D {datadir} -m f'.format(
                pg_ctl=self.executable,
                datadir=self.datadir,
                port=self.port,
                unixsocketdir=self.unixsocketdir
            ),
            shell=True)
