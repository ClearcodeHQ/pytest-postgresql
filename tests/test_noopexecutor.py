from pytest_postgresql.factories import NoopExecutor


def test_nooproc_version(postgresql_proc):
    postgresql_nooproc = NoopExecutor(
        postgresql_proc.host,
        postgresql_proc.port,
        postgresql_proc.user,
        postgresql_proc.options
    )
    assert postgresql_proc == postgresql_nooproc.version