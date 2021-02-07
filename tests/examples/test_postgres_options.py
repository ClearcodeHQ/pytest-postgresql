"""This is not called directly but is used in another test."""


def test_postgres_options(postgresql):
    cur = postgresql.cursor()
    cur.execute('SHOW max_connections')
    assert cur.fetchone() == ('10',)
