"""Helping loader function."""

from typing import Any

import psycopg
from psycopg import Connection


def load_database(**kwargs: Any) -> None:
    """Prepare the database for tests."""
    db_connection: Connection = psycopg.connect(**kwargs)
    with db_connection.cursor() as cur:
        cur.execute("CREATE TABLE stories (id serial PRIMARY KEY, name varchar);")
        cur.execute(
            "INSERT INTO stories (name) VALUES"
            "('Silmarillion'), ('Star Wars'), ('The Expanse'), ('Battlestar Galactica')"
        )
        db_connection.commit()
