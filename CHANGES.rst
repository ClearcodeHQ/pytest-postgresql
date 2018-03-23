CHANGELOG
=========

1.3.4
-------

- [bugfix] properly detect if executor running and clean after executor is being stopped

    .. note::

        Previously if a test failed, there was a possibility of the executor being removed when python was closing,
        causing it to print ignored errors on already unloaded modules.

1.3.3
-------

- [enhancement] use executor's context manager to start/stop postrgesql server in a fixture

1.3.2
-------

- [bugfix] version regexp to correctly catch postgresql 10

1.3.1
-------

- [enhancement] explicitly turn off logging_collector

1.3.0
-------

- [feature] pypy compatibility

1.2.0
-------

- [bugfix] - disallow connection to database before it gets dropped.

    .. note::

        Otherwise it caused random test subprocess to connect again and this the drop was unsucessfull which resulted in many more test failes on setup.

- [cleanup] - removed path.py dependency

1.1.1
-------

- [bugfix] - Fixing the default pg_ctl path creation

1.1.0
-------

- [feature] - migrate usage of getfuncargvalue to getfixturevalue. require at least pytest 3.0.0

1.0.0
-------

- create command line and pytest.ini configuration options for postgresql starting parameters
- create command line and pytest.ini configuration options for postgresql username
- make the port random by default
- create command line and pytest.ini configuration options for executable
- create command line and pytest.ini configuration options for host
- create command line and pytest.ini configuration options for port
- Extracted code from pytest-dbfixtures
