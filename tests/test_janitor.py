"""Database Janitor tests."""
from unittest.mock import patch
import pytest
from pkg_resources import parse_version

from pytest_postgresql.janitor import DatabaseJanitor

VERSION = parse_version("9.6")


@pytest.mark.parametrize("version", (VERSION, 9.6, "9.6"))
def test_version_cast(version):
    """Test that version is cast to Version object."""
    janitor = DatabaseJanitor(None, None, None, None, version)
    assert janitor.version == VERSION


@patch("pytest_postgresql.janitor.psycopg2.connect")
def test_cursor_selects_postgres_database(connect_mock):
    """Test that the cursor requests the postgres database."""
    janitor = DatabaseJanitor("user", "host", "1234", "database_name", 9.6)
    with janitor.cursor():
        connect_mock.assert_called_once_with(
            dbname="postgres", user="user", password=None, host="host", port="1234"
        )


@patch("pytest_postgresql.janitor.psycopg2.connect")
def test_cursor_connects_with_password(connect_mock):
    """Test that the cursor requests the postgres database."""
    janitor = DatabaseJanitor("user", "host", "1234", "database_name", 9.6, "some_password")
    with janitor.cursor():
        connect_mock.assert_called_once_with(
            dbname="postgres", user="user", password="some_password", host="host", port="1234"
        )
