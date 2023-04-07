from typing import Any

from pytest_postgresql.compat import psycopg


def loader(sql_filename: str, **kwargs: Any) -> None:
    """Database loader for sql files"""
    db_connection = psycopg.connect(**kwargs)
    with open(sql_filename, "r") as _fd:
        with db_connection.cursor() as cur:
            cur.execute(_fd.read())
    db_connection.commit()
