"""Auxiliary tests."""
import pytest

from pytest_postgresql.executor import PostgreSQLExecutor


@pytest.mark.parametrize(
    "ctl_input, version",
    (
        ("pg_ctl (PostgreSQL) 9.6.21", "9.6"),
        ("pg_ctl (PostgreSQL) 10.0", "10.0"),
        ("pg_ctl (PostgreSQL) 10.1", "10.1"),
        ("pg_ctl (PostgreSQL) 10.16", "10.16"),
        ("pg_ctl (PostgreSQL) 11.11", "11.11"),
        ("pg_ctl (PostgreSQL) 12.6", "12.6"),
        ("pg_ctl (PostgreSQL) 13.2", "13.2"),
    ),
)
def test_versions(ctl_input: str, version: str) -> None:
    """Check correctness of the version regexp."""
    match = PostgreSQLExecutor.VERSION_RE.search(ctl_input)
    assert match is not None
    assert match.groupdict()["version"] == version
