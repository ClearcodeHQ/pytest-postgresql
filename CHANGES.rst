CHANGELOG
=========

4.1.1
----------

Misc
++++

- Error message typo fix
- Docker documentation example typo fixes
- Have setuptools required as package dependency. pkg_resources.parse_version is used in code 
  but setuptools was only used as build requirements

4.1.0
----------

Features
++++++++

- Import FixtureRequest from pytest, not private _pytest.
  Require at least pytest 6.2
- Replace tmpdir_factory with tmp_path_factory

4.0.0
----------

Features
++++++++

- Upgrade to psycopg 3.
- Xdist running test connecting to already existing postgresql,
  will now create separate databases for each worker.

Backward Incompatibilities
++++++++++++++++++++++++++

- Use psycopg 3 and return its connections in client fixtures.
- Drop support for postgresql 9.6
- client fixture will no longer utilize configuration's load param
- client fixture will no longer utilize configuration's dbanme parameter

Misc
++++

- Add Postgresql 14 to the CI

3.1.2
----------

Bugfix
++++++

- Database can be created by DatabaseJanitor or the client fixture when an isolation
  level is specified.

3.1.1
----------

Misc
++++

- rely on `get_port` functionality delivered by `port_for`

3.1.0
----------

Features
++++++++

- Added type annotations and compatibitlity with PEP 561

Misc
++++

- pre-commit configuration

3.0.2
----------

Bugfix
++++++

- Changed `UPDATE pg_database SET` to `ALTER`. System tables should not be updated.

3.0.1
----------

Bugfix
++++++

- Fixed DatabaseJanitor port type hint to int from str
- Changed retry definition to not fail if psycopg2 is not installed.
  Now the default is Exception.

Misc
++++

- Support python 3.7 and up

3.0.0
----------

Features
++++++++

- Ability to create template database once for the process fixture and
  re-recreate a clean database out of it every test. Not only it does provide some
  common db initialisation between tests but also can speed up tests significantly,
  especially if the initialisation has lots of operations to perform.
- DatabaseJanitor can now define a `connection_timeout` parameter.
  How long will it try to connect to database before raising a TimeoutError
- Updated supported python versions
- Unified temporary directory handling in fixture. Settled on tmpdir_factory.
- Fully moved to the Github Actions as CI/CD pipeline

Deprecations
++++++++++++

- Deprecated support for `logs_prefix` process fixture factory argument,
  `--postgresql-logsprefix` pytest command line option and `postgresql_logsprefix`
  ini configuration option. tmpdir_factory now builds pretty unique temporary directory structure.

Backward Incompatibilities
++++++++++++++++++++++++++

- Dropped support for postgresql 9.5 and down
- Removed init_postgresql_database and drop_postgresql_database functions.
  They were long deprecated and their role perfectly covered by DatabaseJanitor class.
- `pytest_postgresql.factories.get_config` was moved to `pytest_postgresql.config.get_config`
- all `db_name` keywords and attributes were renamed to `dbname`
- postgresql_nooproc fixture was renamed to postgresql_noproc

Bugfix
++++++

- Use `postgresql_logsprefix` and `--postgresql-logsprefix` again.
  They were stopped being used somewhere along the way.
- Sometimes pytest-postrgesql would fail to start postgresql with
  "FATAL:  the database system is starting up" message. It's not really a fatal error,
  but a message indicating that the process still starts. Now pytest-postgresql will wait properly in this cases.

2.6.1
----------

- [bugfix] To not fail loading code if no postgresql version is installed.
  Fallback for janitor and process fixture only, if called upon.

2.6.0
----------

- [enhancement] add ability to pass options to pg_ctl's -o flag to send arguments to the underlying postgres executable 
  Use `postgres_options` as fixture argument, `--postgresql-postgres-options` as pytest starting option or
  `postgresql_postgres_options` as pytest.ini configuration option

2.5.3
----------

- [enhancement] Add ability to set up isolation level for fixture and janitor

2.5.2
----------

- [fix] Status checks for running postgres depend on pg_ctl status code,
  not on pg_ctl log language. Fixes starting on systems without C locale.
  Thanks @Martin Meyries.


2.5.1
----------

- [fix] Added LC_* env vars to running initdb and other utilities.
  Now all tools and server are using same, C locale


2.5.0
----------

- [feature] Ability to define default schema to initialize database with
- [docs] Added more examples to readme on how to use the plugin


2.4.1
----------

- [enhancement] extract NoopExecutor into it's own submodule
- [bugfix] Ignore occasional `ProcessFinishedWithError` error on executor exit.
- [bugfix] Fixed setting custom password for process fixture
- [bugfix] Fix version detection, to allow for two-digit minor version part

2.4.0
----------

- [feature] Drop support for python 3.5
- [enhancement] require at least mirakuru 2.3.0 (executor's stop method parameter's change)
- [bug] pass password to DatabaseJanitor in client's factory

2.3.0
----------

- [feature] Allow to set password for postgresql. Use it throughout the flow.
- [bugfix] Default Janitor's connections to postgres database. When using custom users, 
  postgres attempts to use user's database and it might not exist.
- [bugfix] NoopExecutor connects to read version by context manager to properly handle cases
  where it can't connect to the server.

2.2.1
----------

- [bugfix] Fix drop_postgresql_database to actually use DatabaseJanitor.drop instead of an init

2.2.0
----------

- [feature] ability to properly connect to already existing postgresql server using ``postgresql_nooproc`` fixture.

2.1.0
----------

- [enhancement] Gather helper functions maintaining postgresql database in DatabaseJanitor class.
- [deprecate] Deprecate ``init_postgresql_database`` in favour of ``DatabaseJanitor.init``
- [deprecate] Deprecate ``drop_postgresql_database`` in favour of ``DatabaseJanitor.drop``

2.0.0
----------

- [feature] Drop support for python 2.7. From now on, only support python 3.5 and up
- [feature] Ability to configure database name through plugin options
- [enhancement] Use tmpdir_factory. Drop ``logsdir`` parameter
- [ehnancement] Support only Postgresql 9.0 and up
- [bugfix] Always start postgresql with LC_ALL, LC_TYPE and LANG set to C.UTF-8.
  It makes postgresql start in english.

1.4.1
----------

- [bugfix] Allow creating test database with hyphens 

1.4.0
----------

- [enhancements] Ability to configure additional options for postgresql process and connection
- [bugfix] - removed hard dependency on ``psycopg2``, allowing any of its alternative packages, like
  ``psycopg2-binary``, to be used.
- [maintenance] Drop support for python 3.4 and use 3.7 instead

1.3.4
----------

- [bugfix] properly detect if executor running and clean after executor is being stopped

    .. note::

        Previously if a test failed, there was a possibility of the executor being removed when python was closing,
        causing it to print ignored errors on already unloaded modules.

1.3.3
----------

- [enhancement] use executor's context manager to start/stop postrgesql server in a fixture

1.3.2
----------

- [bugfix] version regexp to correctly catch postgresql 10

1.3.1
----------

- [enhancement] explicitly turn off logging_collector

1.3.0
----------

- [feature] pypy compatibility

1.2.0
----------

- [bugfix] - disallow connection to database before it gets dropped.

    .. note::

        Otherwise it caused random test subprocess to connect again and this the drop was unsuccessful which resulted in many more test fails on setup.

- [cleanup] - removed path.py dependency

1.1.1
----------

- [bugfix] - Fixing the default pg_ctl path creation

1.1.0
----------

- [feature] - migrate usage of getfuncargvalue to getfixturevalue. require at least pytest 3.0.0

1.0.0
----------

- create command line and pytest.ini configuration options for postgresql starting parameters
- create command line and pytest.ini configuration options for postgresql username
- make the port random by default
- create command line and pytest.ini configuration options for executable
- create command line and pytest.ini configuration options for host
- create command line and pytest.ini configuration options for port
- Extracted code from pytest-dbfixtures
