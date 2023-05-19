"""Plugin's configuration."""
from typing import Any, List, Optional, TypedDict

from pytest import FixtureRequest


class PostgresqlConfigDict(TypedDict):
    """Typed Config dictionary."""

    exec: str
    host: str
    port: Optional[str]
    user: str
    password: str
    options: str
    startparams: str
    unixsocketdir: str
    dbname: str
    load: List[str]
    postgres_options: str


def get_config(request: FixtureRequest) -> PostgresqlConfigDict:
    """Return a dictionary with config options."""

    def get_postgresql_option(option: str) -> Any:
        name = "postgresql_" + option
        return request.config.getoption(name) or request.config.getini(name)

    return PostgresqlConfigDict(
        exec=get_postgresql_option("exec"),
        host=get_postgresql_option("host"),
        port=get_postgresql_option("port"),
        user=get_postgresql_option("user"),
        password=get_postgresql_option("password"),
        options=get_postgresql_option("options"),
        startparams=get_postgresql_option("startparams"),
        unixsocketdir=get_postgresql_option("unixsocketdir"),
        dbname=get_postgresql_option("dbname"),
        load=get_postgresql_option("load"),
        postgres_options=get_postgresql_option("postgres_options"),
    )
