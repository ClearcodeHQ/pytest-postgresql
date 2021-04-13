from pytest_postgresql import factories

postgresql_my_proc = factories.postgresql_noproc()
postgres_with_schema = factories.postgresql(
    "postgresql_my_proc", db_name="test", load=["tests/test_sql/eidastats.sql"]
)


def test_postgres_docker_load(postgres_with_schema):
    """
    Check main postgres fixture
    """
    with postgres_with_schema.cursor() as cur:
        # Query for public.tokens since the eidastats changes postgres' search_path to ''.
        # The search path by default is public, but without it,
        # every schema has to be written explicitly.
        cur.execute("select * from public.tokens")
        print(cur.fetchall())
