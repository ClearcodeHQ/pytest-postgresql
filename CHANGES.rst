CHANGELOG
=========

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
