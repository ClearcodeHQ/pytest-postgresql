Contribute to pytest-postgresql
==============

Thank you for taking time to contribute to pytest-postgresql!

The following is a set of guidelines for contributing to pytest-postgresql. These are just guidelines, not rules, use your best judgment and feel free to propose changes to this document in a pull request.

Bug Reports
-----------

#. Use a clear and descriptive title for the issue - it'll be much easier to identify the problem.
#. Describe the steps to reproduce the problems in as many details as possible.
#. If possible, provide a code snippet to reproduce the issue.

Feature requests/proposals
--------------------------

#. Use a clear and descriptive title for the proposal
#. Provide as detailed description as possible
    * Use case is great to have
#. There'll be a bit of discussion for the feature. Don't worry, if it is to be accepted, we'd like to support it, so we need to understand it thoroughly.
  

Pull requests
-------------

#. Start with a bug report or feature request
#. Use a clear and descriptive title
#. Provide a description - which issue does it refers to, and what part of the issue is being solved
#. Be ready for code review :)

Commits
-------

#. Make sure commits are atomic, and each atomic change is being followed by test.
#. If the commit solves part of the issue reported, include *refs #[Issue number]* in a commit message.
#. If the commit solves whole issue reported, please refer to `Closing issues via commit messages <https://help.github.com/articles/closing-issues-via-commit-messages/>`_ for ways to close issues when commits will be merged.


Coding style
------------

#. Coding style is being handled by black and doublechecked by flake8 and pydocstyle
    * We provide a `pre-commit <https://pre-commit.com/>`_ configuration for invoking these on commit.

Testing
-------

# Tests are writen using pytest.
# PR tests run on Github Actions.
# In order to run the tests locally you need to have one version of postgres installed. And pass envvar named `POSTGRES` with used version number
# If you encounter any test failures due to locale issues, make sure that both `en_US.UTF-8` and `de_DE.UTF-8` are enabled in `/etc/locale.gen` and then run `sudo locale-gen`.
