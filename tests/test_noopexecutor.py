"""Test for NoopExecutor."""

from pytest_postgresql.factories import NoopExecutor


def test_nooproc_version(postgresql_proc):
    """Test the wya postgresql version is being read."""
    postgresql_nooproc = NoopExecutor(
        postgresql_proc.host,
        postgresql_proc.port,
        postgresql_proc.user,
        postgresql_proc.options
    )
    assert postgresql_proc.version == postgresql_nooproc.version
