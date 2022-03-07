from typing import Dict

from pytest_postgresql.compat import psycopg2


def loader(sql_filename: str, **kwargs: Dict) -> None:
    """Database loader for sql files"""
    db_connection = psycopg2.connect(**kwargs)
    with open(sql_filename, "r") as _fd:
        with db_connection.cursor() as cur:
            cur.execute(_fd.read())
    db_connection.commit()
