"""Helping loader function."""

from pytest_postgresql.compat import connection, psycopg2


def load_database(**kwargs: str) -> None:
    db_connection: connection = psycopg2.connect(**kwargs)
    with db_connection.cursor() as cur:
        cur.execute("CREATE TABLE stories (id serial PRIMARY KEY, name varchar);")
        cur.execute(
            "INSERT INTO stories (name) VALUES"
            "('Silmarillion'), ('Star Wars'), ('The Expanse'), ('Battlestar Galactica')"
        )
        db_connection.commit()
