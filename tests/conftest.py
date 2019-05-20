"""Tests main conftest file."""
from pytest_postgresql import factories


PG_CTL = '/usr/lib/postgresql/{ver}/bin/pg_ctl'

# pylint:disable=invalid-name
postgresql92 = factories.postgresql_proc(PG_CTL.format(ver='9.2'), port=None)
postgresql93 = factories.postgresql_proc(PG_CTL.format(ver='9.3'), port=None)
postgresql94 = factories.postgresql_proc(PG_CTL.format(ver='9.4'), port=None)
postgresql95 = factories.postgresql_proc(PG_CTL.format(ver='9.5'), port=None)
postgresql96 = factories.postgresql_proc(PG_CTL.format(ver='9.6'), port=None)
postgresql10 = factories.postgresql_proc(PG_CTL.format(ver='10'), port=None)
postgresql101 = factories.postgresql_proc(PG_CTL.format(ver='10.1'), port=None)

postgresql_proc2 = factories.postgresql_proc(port=9876)
postgresql2 = factories.postgresql('postgresql_proc2', db_name='test-db')

postgresql_rand_proc = factories.postgresql_proc(port=None)
postgresql_rand = factories.postgresql('postgresql_rand_proc')
# pylint:enable=invalid-name
