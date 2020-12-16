"""Tests main conftest file."""
import os
from pytest_postgresql import factories

pytest_plugins = ['pytester']

PG_CTL = '/usr/lib/postgresql/{ver}/bin/pg_ctl'
TEST_SQL_DIR = os.path.dirname(os.path.abspath(__file__)) + '/test_sql/'

# pylint:disable=invalid-name
postgresql95 = factories.postgresql_proc(PG_CTL.format(ver='9.5'), port=None)
postgresql96 = factories.postgresql_proc(PG_CTL.format(ver='9.6'), port=None)
postgresql10 = factories.postgresql_proc(PG_CTL.format(ver='10'), port=None)
postgres10 = factories.postgresql('postgresql10')
postgresql11 = factories.postgresql_proc(PG_CTL.format(ver='11'), port=None)
postgresql12 = factories.postgresql_proc(PG_CTL.format(ver='12'), port=None)
postgresql13 = factories.postgresql_proc(PG_CTL.format(ver='13'), port=None)

postgresql_proc2 = factories.postgresql_proc(port=9876)
postgresql2 = factories.postgresql('postgresql_proc2', db_name='test-db')
postgresql_load_1 = factories.postgresql('postgresql_proc2', db_name='test-db',
                                         load=[TEST_SQL_DIR + 'test.sql', ])
postgresql_load_2 = factories.postgresql('postgresql_proc2', db_name='test-db',
                                         load=[TEST_SQL_DIR + 'test.sql',
                                               TEST_SQL_DIR + 'test2.sql'])

postgresql_rand_proc = factories.postgresql_proc(port=None)
postgresql_rand = factories.postgresql('postgresql_rand_proc')

postgresql_max_conns_proc = factories.postgresql_proc(postgres_options='-N 10')
postgres_max_conns = factories.postgresql('postgresql_max_conns_proc')
# pylint:enable=invalid-name
