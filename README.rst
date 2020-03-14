.. image:: https://raw.githubusercontent.com/ClearcodeHQ/pytest-postgresql/master/logo.png
    :width: 100px
    :height: 100px
    
pytest-postgresql
=================

.. image:: https://img.shields.io/pypi/v/pytest-postgresql.svg
    :target: https://pypi.python.org/pypi/pytest-postgresql/
    :alt: Latest PyPI version

.. image:: https://img.shields.io/pypi/wheel/pytest-postgresql.svg
    :target: https://pypi.python.org/pypi/pytest-postgresql/
    :alt: Wheel Status

.. image:: https://img.shields.io/pypi/pyversions/pytest-postgresql.svg
    :target: https://pypi.python.org/pypi/pytest-postgresql/
    :alt: Supported Python Versions

.. image:: https://img.shields.io/pypi/l/pytest-postgresql.svg
    :target: https://pypi.python.org/pypi/pytest-postgresql/
    :alt: License

Package status
--------------

.. image:: https://travis-ci.org/ClearcodeHQ/pytest-postgresql.svg?branch=v2.2.1
    :target: https://travis-ci.org/ClearcodeHQ/pytest-postgresql
    :alt: Tests

.. image:: https://coveralls.io/repos/ClearcodeHQ/pytest-postgresql/badge.png?branch=v2.2.1
    :target: https://coveralls.io/r/ClearcodeHQ/pytest-postgresql?branch=v2.2.1
    :alt: Coverage Status

What is this?
=============

This is a pytest plugin, that enables you to test your code that relies on a running PostgreSQL Database.
It allows you to specify fixtures for PostgreSQL process and client.

How to use
==========

.. warning::

    Tested on PostgreSQL versions > 9.x. See tests for more details.

Install with:

.. code-block:: sh

    pip install pytest-postgresql

You will also need to install ``psycopg2``, or one of its alternative packagings such as ``psycopg2-binary``
(pre-compiled wheels) or ``psycopg2cffi`` (CFFI based, useful on PyPy).

Plugin contains three fixtures:

* **postgresql** - it's a client fixture that has functional scope. After each test it ends all leftover connections, and drops test database from PostgreSQL ensuring repeatability.
* **postgresql_proc** - session scoped fixture, that starts PostgreSQL instance at it's first use and stops at the end of the tests.
* **postgresql_nooproc** - a nooprocess fixture, that's connecting to already running postgresql

Simply include one of these fixtures into your tests fixture list.

You can also create additional postgresql client and process fixtures if you'd need to:


.. code-block:: python

    from pytest_postgresql import factories

    postgresql_my_proc = factories.postgresql_proc(
        port=None, unixsocketdir='/var/run')
    postgresql_my = factories.postgresql('postgresql_my_proc')

.. note::

    Each PostgreSQL process fixture can be configured in a different way than the others through the fixture factory arguments.

Connecting to already existing postgresql database
--------------------------------------------------

Some projects are using already running postgresql servers (ie on docker instances).
In order to connect to them, one would be using the ``postgresql_nooproc`` fixture.

.. code-block:: python

    postgresql_external = factories.postgresql('postgresql_nooproc')

By default the  ``postgresql_nooproc`` fixture would connect to postgresql instance using **5432** port. Standard configuration options apply to it.

These are the configuration options that are working on all levels with the ``postgresql_nooproc`` fixture:

Configuration
=============

You can define your settings in three ways, it's fixture factory argument, command line option and pytest.ini configuration option.
You can pick which you prefer, but remember that these settings are handled in the following order:

    * ``Fixture factory argument``
    * ``Command line option``
    * ``Configuration option in your pytest.ini file``


.. list-table:: Configuration options
   :header-rows: 1

   * - PostgreSQL option
     - Fixture factory argument
     - Command line option
     - pytest.ini option
     - Noop process fixture
     - Default
   * - Path to executable
     - executable
     - --postgresql-exec
     - postgresql_exec
     - -
     - /usr/lib/postgresql/9.1/bin/pg_ctl
   * - host
     - host
     - --postgresql-host
     - postgresql_host
     - yes
     - 127.0.0.1
   * - port
     - port
     - --postgresql-port
     - postgresql_port
     - yes (5432)
     - random
   * - postgresql user
     - user
     - --postgresql-user
     - postgresql_user
     - yes
     - postgres
   * - password
     - password
     - --postgresql-password
     - postgresql_password
     - yes
     -
   * - Starting parameters
     - startparams
     - --postgresql-startparams
     - postgresql_startparams
     - -
     - -w
   * - Log filename's prefix
     - logsprefix
     - --postgresql-logsprefix
     - postgresql_logsprefix
     - -
     -
   * - Location for unixsockets
     - unixsocket
     - --postgresql-unixsocketdir
     - postgresql_unixsocketdir
     - -
     - $TMPDIR
   * - Database name
     - db_name
     - --postgresql-dbname
     - postgresql_dbname
     - -
     - test
   * - PostgreSQL connection options
     - options
     - --postgresql-options
     - postgresql_options
     - yes
     -


Example usage:

* pass it as an argument in your own fixture

    .. code-block:: python

        postgresql_proc = factories.postgresql_proc(
            port=8888)

* use ``--postgresql-port`` command line option when you run your tests

    .. code-block::

        py.test tests --postgresql-port=8888


* specify your port as ``postgresql_port`` in your ``pytest.ini`` file.

    To do so, put a line like the following under the ``[pytest]`` section of your ``pytest.ini``:

    .. code-block:: ini

        [pytest]
        postgresql_port = 8888

Maintaining database state outside of the fixtures
--------------------------------------------------

It is possible and appears it's used in other libraries for tests,
to maintain database state with the use of the ``pytest-postgresql`` database
managing functionality:

For this import DatabaseJanitor and use it's init and drop methods:


.. code-block:: python

    from pytest_postgresql.factories import DatabaseJanitor

    # variable definition

    janitor = DatabaseJanitor(user, host, port, db_name, version)
    janitor.init()
    # your code, or yield
    janitor.drop()
    # at this moment you'll have clean database step

or use it as a context manager:

.. code-block:: python

    from pytest_postgresql.factories import DatabaseJanitor

    # variable definition

    with DatabaseJanitor(user, host, port, db_name, version):
        # do something here

Package resources
-----------------

* Bug tracker: https://github.com/ClearcodeHQ/pytest-postgresql/issues

