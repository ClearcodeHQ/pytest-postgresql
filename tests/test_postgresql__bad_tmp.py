from typing import Union

import pytest
import tests.test_postgresql


@pytest.fixture(scope="session")
def tmp_path_factory(tmp_path_factory: Union[pytest.TempPathFactory]):
    r"""overrides the pytest factory to include the \ character"""
    with tmp_path_factory.mktemp(r"bad\path") as tmp:
        pytest.TempPathFactory(tmp, retention_count=0, retention_policy="none", trace=None)


# we want to redo this test but with the custom tmp_path_factory (\)
test_postgresql_proc__bad_path = tests.test_postgresql.test_postgresql_proc
