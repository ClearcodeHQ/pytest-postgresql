"""Tests main conftest file."""
import os

from pytest_postgresql import factories
from pytest_postgresql.plugin import *  # noqa: F403,F401

pytest_plugins = ["pytester"]
POSTGRESQL_VERSION = os.environ.get("POSTGRES", "13")


TEST_SQL_DIR = os.path.dirname(os.path.abspath(__file__)) + "/test_sql/"

postgresql_proc2 = factories.postgresql_proc(port=None)
postgresql2 = factories.postgresql("postgresql_proc2", dbname="test-db")
postgresql_load_1 = factories.postgresql(
    "postgresql_proc2",
    dbname="test-load-db",
    load=[
        TEST_SQL_DIR + "test.sql",
    ],
)
postgresql_load_2 = factories.postgresql(
    "postgresql_proc2",
    dbname="test-load-moredb",
    load=[TEST_SQL_DIR + "test.sql", TEST_SQL_DIR + "test2.sql"],
)
