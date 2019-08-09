import pytest
from pkg_resources import parse_version

from pytest_postgresql.janitor import DatabaseJanitor

VERSION = parse_version('9.2')


@pytest.mark.parametrize('v', (VERSION, 9.2, '9.2'))
def test_version_cast(v):
    """Test that version is cast to Version object."""
    janitor = DatabaseJanitor(None, None, None, None, v)
    assert janitor.version == VERSION
