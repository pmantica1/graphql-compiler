
Contributing Guide
==================

Thank you for taking the time to contribute to this project!

Getting Started
---------------

To get started, make sure that you have ``pipenv``\ , ``docker`` and ``docker-compose`` installed
on your computer. Additionally, since this is a package that supports both Python 2 and Python 3,
please make sure you have Python 2.7.15+ and Python 3.6+ installed locally. This project assumes
that they are available on the system as ``python2`` and ``python3``\ , respectively. If you do not
already have them installed, consider doing so using `pyenv <https://github.com/pyenv/pyenv>`_.

Integration tests are run against multiple SQL databases, some of which require dialect specific
installations to be available in the development environment.
Currently this affects MySQL. A compatible driver can be installed on OSX with:

.. code-block:: bash

   brew install mysql

or on Ubuntu with:

.. code-block:: bash

   apt-get install python-mysqldb

For more details on other systems please refer to
`MySQL dialect information <https://docs.sqlalchemy.org/en/latest/dialects/mysql.html>`_.

Once the dev environment is prepared, from the root of the repository, run:

.. code-block::

   docker-compose up -d
   pipenv sync --dev
   pipenv shell

   py.test graphql_compiler/tests

Some snapshot and integration tests take longer to setup, run, and teardown. These can be optionally
skipped during development by running the tests with the ``--skip-slow`` flag:

.. code-block:: bash

   py.test graphql_compiler/tests --skip-slow

If you run into any issues, please consult the TROUBLESHOOTING.md file. If you encounter and resolve
an issue that is not already part of the troubleshooting guide, we'd appreciate it if you open
a pull request and update the guide to make future development easier.

A test method or class can be marked as slow to be skipped in this fashion by decorating with the
``@pytest.mark.slow`` flag.

Style Guide
-----------

This project follows the
`Google Python style guide <https://google.github.io/styleguide/pyguide.html>`_.

Additionally, any contributions must pass the linter ``scripts/lint.sh`` when executed from a
pipenv shell (i.e. after running ``pipenv shell``\ ). To run the linter on changed files only,
commit your changes and run ``scripts/lint.sh --diff``.

Finally, all python files in the repository must display the copyright of the project,
to protect the terms of the license. Please make sure that your files start with a line like:

.. code-block::

   # Copyright 20xx-present Kensho Technologies, LLC.

Python 2 vs Python 3
--------------------

In order to ensure that tests run with a fixed set of packages in both Python 2 and Python 3,
we always run the tests in a virtualenv managed by pipenv. However, since some of our dependencies
have different requirements for Python 2 and Python 3, we have to keep two pipenv lockfiles -- one
per Python version.

We have chosen to make the Python 3 lockfile the default (hence named ``Pipfile.lock``\ ),
since Python 3 offers better performance and we like our tests and linters running quickly.
The Python 2 lockfile is named ``Pipfile.py2.lock``.

If you need to set up a Python 2 virtualenv locally, simply run the following script:

.. code-block::

   ./scripts/make_py2_venv.sh

If you change the Pipfile or the package requirements, please make sure to regenerate the
lockfiles for both Python versions. The easiest way to do so is with the following script:

.. code-block::

   ./scripts/make_pipenv_lockfiles.sh
