"""Test behavior of postgres_options passed in different ways."""

from pathlib import Path

import pytest
from pytest import Pytester

import pytest_postgresql


@pytest.fixture
def pointed_pytester(pytester: Pytester) -> Pytester:
    """Pre-configured pytester fixture."""
    pytest_postgresql_path = Path(pytest_postgresql.__file__)
    root_path = pytest_postgresql_path.parent.parent
    pytester.syspathinsert(root_path)
    pytester.makeconftest("from pytest_postgresql.plugin import *\n")
    return pytester


def test_postgres_options_config_in_cli(pointed_pytester: Pytester) -> None:
    """Check that command line arguments are honored."""
    pointed_pytester.copy_example("test_postgres_options.py")
    ret = pointed_pytester.runpytest(
        "--postgresql-postgres-options", "-N 16", "test_postgres_options.py"
    )
    ret.assert_outcomes(passed=1)


def test_postgres_options_config_in_ini(pointed_pytester: Pytester) -> None:
    """Check that pytest.ini arguments are honored."""
    pointed_pytester.copy_example("test_postgres_options.py")
    pointed_pytester.makefile(".ini", pytest="[pytest]\npostgresql_postgres_options = -N 16\n")
    ret = pointed_pytester.runpytest("test_postgres_options.py")
    ret.assert_outcomes(passed=1)


def test_postgres_loader_in_cli(pointed_pytester: Pytester) -> None:
    """Check that command line arguments are honored."""
    pointed_pytester.copy_example("test_load.py")
    test_sql_path = pointed_pytester.copy_example("test.sql")
    ret = pointed_pytester.runpytest(f"--postgresql-load={test_sql_path}", "test_load.py")
    ret.assert_outcomes(passed=1)
