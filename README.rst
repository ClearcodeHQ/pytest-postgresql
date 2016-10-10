pytest-postgresql
=================

.. image:: https://img.shields.io/pypi/v/pytest-postgresql.svg
    :target: https://pypi.python.org/pypi/pytest-postgresql/

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

.. image:: https://travis-ci.org/ClearcodeHQ/pytest-postgresql.svg?branch=v1.0.0
    :target: https://travis-ci.org/ClearcodeHQ/pytest-postgresql
    :alt: Tests

.. image:: https://coveralls.io/repos/ClearcodeHQ/pytest-postgresql/badge.png?branch=v1.0.0
    :target: https://coveralls.io/r/ClearcodeHQ/pytest-postgresql?branch=v1.0.0
    :alt: Coverage Status

.. image:: https://requires.io/github/ClearcodeHQ/pytest-postgresql/requirements.svg?tag=v1.0.0
     :target: https://requires.io/github/ClearcodeHQ/pytest-postgresql/requirements/?tag=v1.0.0
     :alt: Requirements Status

What is this?
=============

This is a pytest plugin, that enables you to test your code that relies on a running PostgreSQL Database.
It allows you to specify fixtures for PostgreSQL process and client.

How to use
==========

.. warning::

    Tested on PostgreSQL versions > 9.x. See tests for more details.

Plugin contains two fixtures

* **postgresql** - it's a client fixture that has functional scope. After each test it ends all lefover connections, and drops test database from PostgreSQL ensuirng repeatability.
* **postgresql_proc** - session scoped fixture, that starts PostgreSQL instance at it's first use and stops at the end of the tests.

Simply include one of these fixtures into your tests fixture list.

You can also create additional postgresql client and process fixtures if you'd need to:


.. code-block:: python

    from pytest_postgresql import factories

    postgresql_my_proc = factories.postgresql_proc(
        port=None, logsdir='/tmp')
    postgresql_my = factories.postgreesql('postgresql_my_proc')

.. note::

    Each PostgreSQL process fixture can be configured in a different way than the others through the fixture factory arguments.

Configuration
=============

You can define your settings in three ways, it's fixture factory argument, command line option and pytest.ini configuration option.
You can pick which you prefer, but remember that these settings are handled in the following order:

    * ``Fixture factory argument``
    * ``Command line option``
    * ``Configuration option in your pytest.ini file``

+--------------------------+--------------------------+----------------------------+--------------------------+------------------------------------+
| PostgreSQL option        | Fixture factory argument | Command line option        | pytest.ini option        | Default                            |
+==========================+==========================+============================+==========================+====================================+
| Path to executable       | executable               | --postgresql-exec          | postgresql_exec          | /usr/lib/postgresql/9.1/bin/pg_ctl |
+--------------------------+--------------------------+----------------------------+--------------------------+------------------------------------+
| host                     | host                     | --postgresql-host          | postgresql_host          | 127.0.0.1                          |
+--------------------------+--------------------------+----------------------------+--------------------------+------------------------------------+
| port                     | port                     | --postgresql-port          | postgresql_port          | random                             |
+--------------------------+--------------------------+----------------------------+--------------------------+------------------------------------+
| postgresql user          | user                     | --postgresql-user          | postgresql_user          | postgres                           |
+--------------------------+--------------------------+----------------------------+--------------------------+------------------------------------+
| Starting parameters      | startparams              | --postgresql-startparams   | postgresql_startparams   | -w                                 |
+--------------------------+--------------------------+----------------------------+--------------------------+------------------------------------+
| Log directory location   | logsdir                  | --postgresql-logsdir       | postgresql_logsdir       | $TMPDIR                            |
+--------------------------+--------------------------+----------------------------+--------------------------+------------------------------------+
| Log filename's prefix    | logsprefix               | --postgresql-logsprefix    | postgresql_logsprefix    |                                    |
+--------------------------+--------------------------+----------------------------+--------------------------+------------------------------------+
| Location for unixsockets | unixsocket               | --postgresql-unixsocketdir | postgresql_unixsocketdir | $TMPDIR                            |
+--------------------------+--------------------------+----------------------------+--------------------------+------------------------------------+

Example usage:

* pass it as an argument in your own fixture

    .. code-block:: python

        postgresql_proc = factories.postgresql_proc(
            port=8888)

* use ``--postgresql-port`` command line option when you run your tests

    .. code-block::

        py.test tests --postgresql-port=8888


* specify your directory as ``postgresql_port`` in your ``pytest.ini`` file.

    To do so, put a line like the following under the ``[pytest]`` section of your ``pytest.ini``:

    .. code-block:: ini

        [pytest]
        postgresql_port = 8888

Package resources
-----------------

* Bug tracker: https://github.com/ClearcodeHQ/pytest-postgresql/issues

