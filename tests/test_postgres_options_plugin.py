"""Test behavior of postgres_options passed in different ways."""


def test_postgres_options_config_in_cli(pytester):
    """Check that command line arguments are honored."""
    pytester.copy_example("test_postgres_options.py")
    ret = pytester.runpytest("--postgresql-postgres-options", "-N 11", "test_postgres_options.py")
    ret.assert_outcomes(passed=1)


def test_postgres_options_config_in_ini(pytester):
    """Check that pytest.ini arguments are honored."""
    pytester.copy_example("test_postgres_options.py")
    pytester.makefile(".ini", pytest="[pytest]\npostgresql_postgres_options = -N 11\n")
    ret = pytester.runpytest("test_postgres_options.py")
    ret.assert_outcomes(passed=1)
