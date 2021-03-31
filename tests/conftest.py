"""Tests main conftest file."""
import os
import platform
from datetime import datetime, timedelta
from pathlib import Path
from time import sleep

from pytest_postgresql import factories

pytest_plugins = ['pytester']
POSTGRESQL_VERSION = os.environ.get("POSTGRES", "13")
IS_GITHUB_ACTIONS = os.environ.get("GITHUB_ACTIONS", False)


def find_pg_ctl(path: str) -> Path:
    """Find the pg_ctl binary in a subdirectory.

    On macos the path is something like
    /usr/local/Cellar/postgresql@11/11.10/bin/pg_ctl. Since we don't know what
    the minor version will be, glob it instead to find the path.
    """
    return list(Path(path).glob('**/bin/pg_ctl'))[0]


def create_version(ver: str) -> Path:
    """Create postgres version string for macos and linux."""
    # macos
    if platform.system() == 'Darwin':
        if ver == '13':
            # brew installs 13 as postgresql right now
            return find_pg_ctl('/usr/local/Cellar/postgresql/')
        return find_pg_ctl(f'/usr/local/Cellar/postgresql@{ver}/')

    # linux
    return find_pg_ctl(f'/usr/lib/postgresql/{ver}/')


TEST_SQL_DIR = os.path.dirname(os.path.abspath(__file__)) + '/test_sql/'

# pylint:disable=invalid-name
postgresql_proc_version = factories.postgresql_proc(
    create_version(ver=POSTGRESQL_VERSION),
    port=None
)

postgresql_proc2 = factories.postgresql_proc(port=None)
postgresql2 = factories.postgresql('postgresql_proc2', db_name='test-db')
postgresql_load_1 = factories.postgresql('postgresql_proc2', db_name='test-db',
                                         load=[TEST_SQL_DIR + 'test.sql', ])
postgresql_load_2 = factories.postgresql('postgresql_proc2', db_name='test-db',
                                         load=[TEST_SQL_DIR + 'test.sql',
                                               TEST_SQL_DIR + 'test2.sql'])
# pylint:enable=invalid-name
