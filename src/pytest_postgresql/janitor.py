"""Database Janitor."""
import re
from contextlib import contextmanager
from functools import partial
from types import TracebackType
from typing import TypeVar, Union, Optional, Type, Callable, Iterator

from pkg_resources import parse_version

from pytest_postgresql.compat import psycopg, cursor, check_for_psycopg, connection
from pytest_postgresql.retry import retry
from pytest_postgresql.sql import loader

Version = type(parse_version("1"))


DatabaseJanitorType = TypeVar("DatabaseJanitorType", bound="DatabaseJanitor")


class DatabaseJanitor:
    """Manage database state for specific tasks."""

    def __init__(
        self,
        user: str,
        host: str,
        port: Union[str, int],
        dbname: str,
        version: Union[str, float, Version],  # type: ignore[valid-type]
        password: Optional[str] = None,
        isolation_level: "Optional[psycopg.IsolationLevel]" = None,
        connection_timeout: int = 60,
    ) -> None:
        """
        Initialize janitor.

        :param user: postgresql username
        :param host: postgresql host
        :param port: postgresql port
        :param dbname: database name
        :param version: postgresql version number
        :param password: optional postgresql password
        :param isolation_level: optional postgresql isolation level
            defaults to server's default
        :param connection_timeout: how long to retry connection before
            raising a TimeoutError
        """
        self.user = user
        self.password = password
        self.host = host
        self.port = port
        self.dbname = dbname
        self._connection_timeout = connection_timeout
        check_for_psycopg()
        self.isolation_level = isolation_level
        if not isinstance(version, Version):
            self.version = parse_version(str(version))
        else:
            self.version = version

    def init(self) -> None:
        """Create database in postgresql."""
        template_name = f"{self.dbname}_tmpl"
        with self.cursor() as cur:
            if self.dbname.endswith("_tmpl"):
                result = False
            else:
                cur.execute(
                    "SELECT EXISTS "
                    "(SELECT datname FROM pg_catalog.pg_database WHERE datname= %s);",
                    (template_name,),
                )
                row = cur.fetchone()
                result = (row is not None) and row[0]
            if not result:
                cur.execute(f'CREATE DATABASE "{self.dbname}";')
            else:
                # All template database does not allow connection:
                self._dont_datallowconn(cur, template_name)
                # And make sure no-one is left connected to the template database.
                # Otherwise Creating database from template will fail
                self._terminate_connection(cur, template_name)
                cur.execute(f'CREATE DATABASE "{self.dbname}" TEMPLATE "{template_name}";')

    def drop(self) -> None:
        """Drop database in postgresql."""
        # We cannot drop the database while there are connections to it, so we
        # terminate all connections first while not allowing new connections.
        with self.cursor() as cur:
            self._dont_datallowconn(cur, self.dbname)
            self._terminate_connection(cur, self.dbname)
            cur.execute(f'DROP DATABASE IF EXISTS "{self.dbname}";')

    @staticmethod
    def _dont_datallowconn(cur: cursor, dbname: str) -> None:
        cur.execute(f'ALTER DATABASE "{dbname}" with allow_connections false;')

    @staticmethod
    def _terminate_connection(cur: cursor, dbname: str) -> None:
        cur.execute(
            "SELECT pg_terminate_backend(pg_stat_activity.pid)"
            "FROM pg_stat_activity "
            "WHERE pg_stat_activity.datname = %s;",
            (dbname,),
        )

    def load(self, load: Union[Callable, str]) -> None:
        """
        Loads data into a database.

        Either runs a passed loader if it's callback,
        or runs predefined loader if it's sql file.
        """
        if isinstance(load, str):
            if "/" in load:
                _loader: Callable = partial(loader, load)
            else:
                loader_parts = re.split("[.:]", load, 2)
                import_path = ".".join(loader_parts[:-1])
                loader_name = loader_parts[-1]
                _temp_import = __import__(import_path, globals(), locals(), fromlist=[loader_name])
                _loader = getattr(_temp_import, loader_name)
        else:
            _loader = load
        _loader(
            host=self.host,
            port=self.port,
            user=self.user,
            dbname=self.dbname,
            password=self.password,
        )

    @contextmanager
    def cursor(self) -> Iterator[cursor]:
        """Return postgresql cursor."""

        def connect() -> connection:
            return psycopg.connect(
                dbname="postgres",
                user=self.user,
                password=self.password,
                host=self.host,
                port=self.port,
            )

        conn = retry(
            connect, timeout=self._connection_timeout, possible_exception=psycopg.OperationalError
        )
        conn.isolation_level = self.isolation_level
        # We must not run a transaction since we create a database.
        conn.autocommit = True
        cur = conn.cursor()
        try:
            yield cur
        finally:
            cur.close()
            conn.close()

    def __enter__(self: DatabaseJanitorType) -> DatabaseJanitorType:
        self.init()
        return self

    def __exit__(
        self: DatabaseJanitorType,
        exc_type: Optional[Type[BaseException]],
        exc_val: Optional[BaseException],
        exc_tb: Optional[TracebackType],
    ) -> None:
        self.drop()
