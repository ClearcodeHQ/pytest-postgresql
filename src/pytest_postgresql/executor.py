# Copyright (C) 2016-2020 by Clearcode <http://clearcode.cc>
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
"""PostgreSQL executor crafter around pg_ctl."""

import os.path
import platform
import re
import shutil
import subprocess
import tempfile
import time

from pkg_resources import parse_version
from mirakuru import TCPExecutor
from mirakuru.base import ExecutorType
from mirakuru.exceptions import ProcessFinishedWithError

_LOCALE = "C.UTF-8"

if platform.system() == "Darwin":
    _LOCALE = "en_US.UTF-8"


class PostgreSQLUnsupported(Exception):
    """Exception raised when postgresql<9.0 would be detected."""


# pylint:disable=too-many-arguments,too-many-instance-attributes
class PostgreSQLExecutor(TCPExecutor):
    """
    PostgreSQL executor running on pg_ctl.

    Based over an `pg_ctl program
    <http://www.postgresql.org/docs/9.1/static/app-pg-ctl.html>`_
    """

    BASE_PROC_START_COMMAND = ' '.join((
        "{executable} start -D {datadir}",
        "-o \"-F -p {port} -c log_destination='stderr'",
        "-c logging_collector=off -c %s='{unixsocketdir}' {postgres_options}\"",
        "-l {logfile} {startparams}"
    ))

    VERSION_RE = re.compile(r'.* (?P<version>\d+\.\d+)')
    MIN_SUPPORTED_VERSION = parse_version('9.5')

    # pylint:disable=too-many-locals
    def __init__(self, executable, host, port,
                 datadir, unixsocketdir, logfile, startparams,
                 shell=False, timeout=60, sleep=0.1, user='postgres',
                 password='', options='', postgres_options=''):
        """
        Initialize PostgreSQLExecutor executor.

        :param str executable: pg_ctl location
        :param str host: host under which process is accessible
        :param int port: port under which process is accessible
        :param str datadir: path to postgresql datadir
        :param str unixsocketdir: path to socket directory
        :param pathlib.Path logfile: path to logfile for postgresql
        :param str startparams: additional start parameters
        :param bool shell: see `subprocess.Popen`
        :param int timeout: time to wait for process to start or stop.
            if None, wait indefinitely.
        :param float sleep: how often to check for start/stop condition
        :param str user: [default] postgresql's username used to manage
            and access PostgreSQL
        :param str password: optional password for the user
        :param str options:
        :param str postgres_options: extra arguments to `postgres start`
        """
        self._directory_initialised = False
        self.executable = executable
        self.user = user
        self.password = password
        self.options = options
        self.datadir = datadir
        self.unixsocketdir = unixsocketdir
        self.logfile = logfile
        self.startparams = startparams
        self.postgres_options = postgres_options
        command = self.proc_start_command().format(
            executable=self.executable,
            datadir=self.datadir,
            port=port,
            unixsocketdir=self.unixsocketdir,
            logfile=self.logfile,
            startparams=self.startparams,
            postgres_options=self.postgres_options
        )
        super().__init__(
            command,
            host,
            port,
            shell=shell,
            timeout=timeout,
            sleep=sleep,
            envvars={
                "LC_ALL": _LOCALE,
                "LC_CTYPE": _LOCALE,
                "LANG": _LOCALE,
            }
        )
    # pylint:enable=too-many-locals

    def start(self: ExecutorType) -> ExecutorType:
        """Add check for postgresql version before starting process."""
        if self.version < self.MIN_SUPPORTED_VERSION:
            raise PostgreSQLUnsupported(
                'Your version of PostgreSQL is not supported. '
                'Consider updating to PostgreSQL {0} at least. '
                'The currently installed version of PostgreSQL: {1}.'
                .format(self.MIN_SUPPORTED_VERSION, self.version)
            )
        self.init_directory()
        return super().start()

    def clean_directory(self):
        """Remove directory created for postgresql run."""
        if os.path.isdir(self.datadir):
            shutil.rmtree(self.datadir)
        self._directory_initialised = False

    def init_directory(self):
        """
        Initialize postgresql data directory.

        See `Initialize postgresql data directory
            <www.postgresql.org/docs/9.5/static/app-initdb.html>`_
        """
        # only make sure it's removed if it's handled by this exact process
        if self._directory_initialised:
            return
        # remove old one if exists first.
        self.clean_directory()
        init_directory = [self.executable, 'initdb', '--pgdata', self.datadir]
        options = ['--username=%s' % self.user]

        if self.password:
            with tempfile.NamedTemporaryFile() as password_file:
                options += ['--auth=password',
                            '--pwfile=%s' % password_file.name]
                if hasattr(self.password, 'encode'):
                    password = self.password.encode('utf-8')
                else:
                    password = self.password
                password_file.write(password)
                password_file.flush()
                init_directory += ['-o', ' '.join(options)]
                subprocess.check_output(init_directory)
        else:
            options += ['--auth=trust']
            init_directory += ['-o', ' '.join(options)]
            subprocess.check_output(init_directory)

        self._directory_initialised = True

    def wait_for_postgres(self):
        """Wait for postgresql being started."""
        if '-w' not in self.startparams:
            return
        # wait until server is running
        while 1:
            if self.running():
                break
            time.sleep(1)

    def proc_start_command(self):
        """Based on postgres version return proper start command."""
        if self.version > parse_version('9.2'):
            unix_socket_dir_arg_name = 'unix_socket_directories'
        else:
            unix_socket_dir_arg_name = 'unix_socket_directory'
        return self.BASE_PROC_START_COMMAND % unix_socket_dir_arg_name

    @property
    def version(self):
        """Detect postgresql version."""
        version_string = subprocess.check_output(
            [self.executable, '--version']).decode('utf-8')
        matches = self.VERSION_RE.search(version_string)
        return parse_version(matches.groupdict()['version'])

    def running(self):
        """Check if server is running."""
        if not os.path.exists(self.datadir):
            return False
        status_code = subprocess.getstatusoutput(
            f'{self.executable} status -D {self.datadir}')[0]
        return status_code == 0

    def stop(self,
             sig: int = None,
             exp_sig: int = None
             ):
        """Issue a stop request to executable."""
        subprocess.check_output(
            '{pg_ctl} stop -D {datadir} -m f'.format(
                pg_ctl=self.executable,
                datadir=self.datadir,
            ),
            shell=True)
        try:
            super().stop(sig, exp_sig)
        except ProcessFinishedWithError:
            # Finished, leftovers ought to be cleaned afterwards anyway
            pass

    def __del__(self):
        """Make sure the directories are properly removed at the end."""
        try:
            super().__del__()
        finally:
            self.clean_directory()
