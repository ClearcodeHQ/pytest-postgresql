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
from typing import TypeVar, Optional, Any, Union

from pkg_resources import parse_version
from mirakuru import TCPExecutor
from mirakuru.exceptions import ProcessFinishedWithError

_LOCALE = "C.UTF-8"

if platform.system() == "Darwin":
    _LOCALE = "en_US.UTF-8"


T = TypeVar("T", bound="PostgreSQLExecutor")


class PostgreSQLUnsupported(Exception):
    """Exception raised when unsupported postgresql would be detected."""


# pylint:disable=too-many-arguments,too-many-instance-attributes
class PostgreSQLExecutor(TCPExecutor):
    """
    PostgreSQL executor running on pg_ctl.

    Based over an `pg_ctl program
    <http://www.postgresql.org/docs/current/static/app-pg-ctl.html>`_
    """

    BASE_PROC_START_COMMAND = (
        "{executable} start -D {datadir} "
        "-o \"-F -p {port} -c log_destination='stderr' "
        "-c logging_collector=off "
        "-c unix_socket_directories='{unixsocketdir}' {postgres_options}\" "
        "-l {logfile} {startparams}"
    )

    VERSION_RE = re.compile(r".* (?P<version>\d+\.\d+)")
    MIN_SUPPORTED_VERSION = parse_version("9.6")

    # pylint:disable=too-many-locals
    def __init__(
        self,
        executable: str,
        host: str,
        port: int,
        datadir: str,
        unixsocketdir: str,
        logfile: str,
        startparams: str,
        shell: bool = False,
        timeout: Optional[int] = 60,
        sleep: float = 0.1,
        user: str = "postgres",
        password: str = "",
        dbname: Optional[str] = None,
        options: str = "",
        postgres_options: str = "",
    ):
        """
        Initialize PostgreSQLExecutor executor.

        :param executable: pg_ctl location
        :param host: host under which process is accessible
        :param port: port under which process is accessible
        :param datadir: path to postgresql datadir
        :param unixsocketdir: path to socket directory
        :param logfile: path to logfile for postgresql
        :param startparams: additional start parameters
        :param shell: see `subprocess.Popen`
        :param timeout: time to wait for process to start or stop.
            if None, wait indefinitely.
        :param sleep: how often to check for start/stop condition
        :param user: postgresql's username used to manage
            and access PostgreSQL
        :param password: optional password for the user
        :param dbname: database name (might not yet exist)
        :param options:
        :param postgres_options: extra arguments to `postgres start`
        """
        self._directory_initialised = False
        self.executable = executable
        self.user = user
        self.password = password
        self.dbname = dbname
        self.options = options
        self.datadir = datadir
        self.unixsocketdir = unixsocketdir
        self.logfile = logfile
        self.startparams = startparams
        self.postgres_options = postgres_options
        command = self.BASE_PROC_START_COMMAND.format(
            executable=self.executable,
            datadir=self.datadir,
            port=port,
            unixsocketdir=self.unixsocketdir,
            logfile=self.logfile,
            startparams=self.startparams,
            postgres_options=self.postgres_options,
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
            },
        )

    # pylint:enable=too-many-locals

    def start(self: T) -> T:
        """Add check for postgresql version before starting process."""
        if self.version < self.MIN_SUPPORTED_VERSION:
            raise PostgreSQLUnsupported(
                f"Your version of PostgreSQL is not supported. "
                f"Consider updating to PostgreSQL {self.MIN_SUPPORTED_VERSION} at least. "
                f"The currently installed version of PostgreSQL: {self.version}."
            )
        self.init_directory()
        return super().start()

    def clean_directory(self) -> None:
        """Remove directory created for postgresql run."""
        if os.path.isdir(self.datadir):
            shutil.rmtree(self.datadir)
        self._directory_initialised = False

    def init_directory(self) -> None:
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
        init_directory = [self.executable, "initdb", "--pgdata", self.datadir]
        options = ["--username=%s" % self.user]

        if self.password:
            with tempfile.NamedTemporaryFile() as password_file:
                options += ["--auth=password", "--pwfile=%s" % password_file.name]
                if hasattr(self.password, "encode"):
                    password = self.password.encode("utf-8")
                else:
                    password = self.password  # type: ignore[assignment]
                password_file.write(password)
                password_file.flush()
                init_directory += ["-o", " ".join(options)]
                subprocess.check_output(init_directory)
        else:
            options += ["--auth=trust"]
            init_directory += ["-o", " ".join(options)]
            subprocess.check_output(init_directory)

        self._directory_initialised = True

    def wait_for_postgres(self) -> None:
        """Wait for postgresql being started."""
        if "-w" not in self.startparams:
            return
        # wait until server is running
        while 1:
            if self.running():
                break
            time.sleep(1)

    @property
    def version(self) -> Any:
        """Detect postgresql version."""
        version_string = subprocess.check_output([self.executable, "--version"]).decode("utf-8")
        matches = self.VERSION_RE.search(version_string)
        assert matches is not None
        return parse_version(matches.groupdict()["version"])

    def running(self) -> bool:
        """Check if server is running."""
        if not os.path.exists(self.datadir):
            return False
        status_code = subprocess.getstatusoutput(f"{self.executable} status -D {self.datadir}")[0]
        return status_code == 0

    def stop(self: T, sig: Optional[int] = None, exp_sig: Optional[int] = None) -> T:
        """Issue a stop request to executable."""
        subprocess.check_output(
            f"{self.executable} stop -D {self.datadir} -m f",
            shell=True,
        )
        try:
            super().stop(sig, exp_sig)
        except ProcessFinishedWithError:
            # Finished, leftovers ought to be cleaned afterwards anyway
            pass
        return self

    def __del__(self) -> None:
        """Make sure the directories are properly removed at the end."""
        try:
            super().__del__()
        finally:
            self.clean_directory()
