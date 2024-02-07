"""Tests for the `build_loader` function."""

from pathlib import Path

from pytest_postgresql.loader import build_loader, sql
from tests.loader import load_database


def test_loader_callables() -> None:
    """Test handling callables in build_loader."""
    assert load_database == build_loader(load_database)
    assert load_database == build_loader("tests.loader:load_database")


def test_loader_sql() -> None:
    """Test returning partial running sql for the sql file path."""
    sql_path = Path("test_sql/eidastats.sql")
    loader_func = build_loader(sql_path)
    assert loader_func.args == (sql_path,)  # type: ignore
    assert loader_func.func == sql  # type: ignore
