"""Test for NoopExecutor."""

from pytest_postgresql.factories import NoopExecutor


def test_nooproc_version_9(postgresql_proc):
    """Test the way postgresql version is being read for versions < 10."""
    postgresql_nooproc = NoopExecutor(
        postgresql_proc.host,
        postgresql_proc.port,
        postgresql_proc.user,
        postgresql_proc.options
    )
    assert postgresql_proc.version == postgresql_nooproc.version


def test_nooproc_version_post_10(postgresql11):
    """Test the way postgresql version is being read for versions >= 10."""
    postgresql_nooproc = NoopExecutor(
        postgresql11.host,
        postgresql11.port,
        postgresql11.user,
        postgresql11.options
    )
    assert postgresql11.version == postgresql_nooproc.version


def test_nooproc_cached_version(postgresql_proc):
    """Test that the version is being cached."""
    postgresql_nooproc = NoopExecutor(
        postgresql_proc.host,
        postgresql_proc.port,
        postgresql_proc.user,
        postgresql_proc.options
    )
    ver = postgresql_nooproc.version
    with postgresql_proc.stopped():
        assert ver == postgresql_nooproc.version
