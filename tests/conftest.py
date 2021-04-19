"""Tests main conftest file."""
import os

from pytest_postgresql import factories

pytest_plugins = ["pytester"]
POSTGRESQL_VERSION = os.environ.get("POSTGRES", "13")


TEST_SQL_DIR = os.path.dirname(os.path.abspath(__file__)) + "/test_sql/"

# pylint:disable=invalid-name
postgresql_proc2 = factories.postgresql_proc(port=None)
postgresql2 = factories.postgresql("postgresql_proc2", db_name="test-db")
postgresql_load_1 = factories.postgresql(
    "postgresql_proc2",
    db_name="test-db",
    load=[
        TEST_SQL_DIR + "test.sql",
    ],
)
postgresql_load_2 = factories.postgresql(
    "postgresql_proc2",
    db_name="test-db",
    load=[TEST_SQL_DIR + "test.sql", TEST_SQL_DIR + "test2.sql"],
)
# pylint:enable=invalid-name
