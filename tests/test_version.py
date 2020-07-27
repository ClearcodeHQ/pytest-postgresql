"""Auxiliary tests."""
import pytest

from pytest_postgresql.executor import PostgreSQLExecutor


@pytest.mark.parametrize('ctl_input, version', (
    ('pg_ctl (PostgreSQL) 9.6.6', '9.6'),
    ('pg_ctl (PostgreSQL) 9.5', '9.5'),
    ('pg_ctl (PostgreSQL) 9.4.1', '9.4'),
    ('pg_ctl (PostgreSQL) 10.0', '10.0'),
    ('pg_ctl (PostgreSQL) 10.1', '10.1'),
    ('pg_ctl (PostgreSQL) 10.13', '10.13'),
))
def test_versions(ctl_input, version):
    """Check correctness of the version regexp."""
    match = PostgreSQLExecutor.VERSION_RE.search(ctl_input)
    assert match.groupdict()['version'] == version
