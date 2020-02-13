CHANGELOG
=========

unreleased
----------

- [bugfix] NoopExecutor connects to read version by context manager to proerly handle cases
  where it can't connect to the server.

2.2.1
----------

- [bugifx] Fix drop_postgresql_database to actually use DatabaseJanitor.drop instead of an init

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

- [bugfix] Allow creating test databse with hyphens 

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

        Otherwise it caused random test subprocess to connect again and this the drop was unsucessfull which resulted in many more test failes on setup.

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
