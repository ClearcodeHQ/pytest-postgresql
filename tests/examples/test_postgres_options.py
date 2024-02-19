"""Options tests.

Not called directly but is used in another test.
"""

from typing import Any


def test_postgres_options(postgresql: Any) -> None:
    """Check if the max_connections is set as defined in master test."""
    cur = postgresql.cursor()
    cur.execute("SHOW max_connections")
    assert cur.fetchone() == ("16",)
