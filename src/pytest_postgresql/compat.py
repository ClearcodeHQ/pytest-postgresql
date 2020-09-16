"""pscypog2 Compatibility module."""
from typing import Any
from platform import python_implementation


try:
    import psycopg2
except ImportError:
    psycopg2 = False

# pylint:disable=unused-import
if not psycopg2:
    # if there's no postgres, just go with the flow.
    # pylint:disable=invalid-name
    cursor = Any
    connection = Any
elif python_implementation() == "PyPy":
    # pylint:disable=import-error
    from psycopg2cffi._impl.cursor import Cursor as cursor
    from psycopg2cffi._impl.connection import Connection as connection
else:
    from psycopg2._psycopg import cursor, connection  # pylint:disable=no-name-in-module
