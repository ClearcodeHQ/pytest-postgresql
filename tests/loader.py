"""Helping loader function."""

from typing import Any

from pytest_postgresql.compat import connection, psycopg


def load_database(**kwargs: Any) -> None:
    """Prepare the database for tests."""
    db_connection: connection = psycopg.connect(**kwargs)
    with db_connection.cursor() as cur:
        cur.execute("CREATE TABLE stories (id serial PRIMARY KEY, name varchar);")
        cur.execute(
            "INSERT INTO stories (name) VALUES"
            "('Silmarillion'), ('Star Wars'), ('The Expanse'), ('Battlestar Galactica')"
        )
        db_connection.commit()
