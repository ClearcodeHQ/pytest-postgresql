"""Test for NoopExecutor."""

from pytest_postgresql.factories import NoopExecutor


def test_nooproc_version(postgresql_proc_version):
    """
    Test the way postgresql version is being read.

    Version behaves differently for postgresql >= 10 and differently for older ones
    """
    postgresql_nooproc = NoopExecutor(
        postgresql_proc_version.host,
        postgresql_proc_version.port,
        postgresql_proc_version.user,
        postgresql_proc_version.options
    )
    assert postgresql_proc_version.version == postgresql_nooproc.version


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
