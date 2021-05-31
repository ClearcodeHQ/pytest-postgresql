"""This is not called directly but is used in another test."""

from typing import Any


def test_postgres_options(postgresql: Any) -> None:
    cur = postgresql.cursor()
    cur.execute("SHOW max_connections")
    assert cur.fetchone() == ("11",)
