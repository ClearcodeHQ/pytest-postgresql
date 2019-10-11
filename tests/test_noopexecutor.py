

def test_nooproc_version(postgresql_proc, postgresql_nooproc):
    assert postgresql_proc == postgresql_nooproc.version