"""Database Janitor tests."""
import pytest
from pkg_resources import parse_version

from pytest_postgresql.janitor import DatabaseJanitor

VERSION = parse_version('9.2')


@pytest.mark.parametrize('version', (VERSION, 9.2, '9.2'))
def test_version_cast(version):
    """Test that version is cast to Version object."""
    janitor = DatabaseJanitor(None, None, None, None, version)
    assert janitor.version == VERSION
