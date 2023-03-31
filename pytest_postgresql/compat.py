"""
psycopg compatibility module.

It should be possible to import pytest-postgresql without errors when psycopg is not
installed (while tests using it will error or be skipped). So import psycopg only here
and check if it's available.
"""
from typing import Any, TYPE_CHECKING


__all__ = ("psycopg", "cursor", "connection", "check_for_psycopg")


try:
    import psycopg
except ImportError:
    psycopg = False  # type: ignore[assignment]
    if not TYPE_CHECKING:
        # if there's no postgres, just go with the flow.
        cursor = Any
        connection = Any

else:
    from psycopg import Cursor as cursor
    from psycopg import Connection as connection


def check_for_psycopg() -> None:
    """
    Function checks whether psycopg was imported.

    Raises ImportError if not.
    """
    if not psycopg:
        raise ImportError("No module named psycopg. Please install psycopg.")
