from typing import Optional, TypedDict

from pytest import FixtureRequest


class PostgresqlConfigDict(TypedDict):
    exec: str
    host: str
    port: Optional[str | int]
    user: str
    password: Optional[str]
    options: str
    startparams: str
    logsprefix: str
    unixsocketdir: str
    dbname: str
    load: Optional[list[str]]
    postgres_options: str


def get_config(request: FixtureRequest) -> PostgresqlConfigDict:
    """Return a dictionary with config options."""

    def get_postgresql_option(option: str):
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
        logsprefix=get_postgresql_option("logsprefix"),
        unixsocketdir=get_postgresql_option("unixsocketdir"),
        dbname=get_postgresql_option("dbname"),
        load=get_postgresql_option("load"),
        postgres_options=get_postgresql_option("postgres_options")
    )
