.. _developers:

Developer Guidelines
####################

We appreciate all types of contributions to pyrh: bug reports, documentation, and new
features. The issue tracker is the best place to start if you are looking for small
issues to get started with. Specifically look for those marked *Needs Contributor*.

Installation
************
* Python 3.7+ is required
* |poetry|_ is used to manage package dependencies
* |pre-commit|_ is used to manage the project's tooling and linting

   * |black|_
   * |flake8|_
   * |isort|_

* |pyenv|_ / |pyenv-virtualenv|_ are great and highly recommended but not covered in
  this guide

.. |poetry| replace:: ``poetry``
.. _poetry: https://python-poetry.org/

.. |pre-commit| replace:: ``pre-commit``
.. _pre-commit: https://pre-commit.com/

.. |black| replace:: ``black``
.. _black: https://black.readthedocs.io/en/stable/

.. |flake8| replace:: ``flake8``
.. _flake8: https://flake8.pycqa.org/

.. |isort| replace:: ``isort``
.. _isort: https://timothycrosley.github.io/isort/

.. |pyenv| replace:: ``pyenv``
.. _pyenv: https://github.com/pyenv/pyenv

.. |pyenv-virtualenv| replace:: ``pyenv-virtualenv``
.. _pyenv-virtualenv: https://github.com/pyenv/pyenv-virtualenv


.. code-block:: console

    $ git clone https://github.com/robinhood-unofficial/pyrh.git
    $ cd Robinhood
    $ brew install poetry
    $ brew install pre-commit
    $ python -m venv pyrh_env
    $ source pyrh_env/bin/activate
    (pyrh_env) $ poetry install
    (pyrh_env) $ pre-commit install

Lint checks are automatically run when you try to push the code. To manually run them
run the following command. If you want to skip the lint check, you can do that by using
``--no-verify`` when committing.

.. code-block:: console

    (pyrh_env) $ pre-commit run -a
    (pyrh_env) $ git commit -am "Some patch commit" --no-verify # will skip lint checks

Running tests and viewing coverage

.. code-block:: console

    (pyrh_env) $ pytest # from the root directory
    (pyrh_env) $ open htmlcov/index.html # opens coverage in browser (on macOS)

Contributing Code Changes
*************************

We operate using pull requests, please branch off of master to submit your changes. Make
sure to go to GitHub fork the project and switch your remotes. Please try to update the
docs and write some initial tests to aid with code review. Once you're all set please
add a towncrier_ file of your changes to the newsfragment directory.

.. _towncrier: https://towncrier.readthedocs.io/en/actual-freaking-docs/quickstart.html

.. code-block:: console

    (pyrh_env) $ git remote set-url origin https://github.com/{YOUR_USER_NAME}/pyrh.git
    (pyrh_env) $ git remote add upstream https://github.com/robinhood-unofficial/pyrh.git
    (pyrh_env) $ git checkout -b some_changes
    (pyrh_env) $ # now make and commit your changes
    (pyrh_env) $ git push  --set-upstream origin some_changes
    (pyrh_env) $ # now go to YOUR fork and submit a pull request upstream

Release
*******

To cut a new release go through the following steps.

* Make sure that the version is updated in both ``__init__.py`` and ``pyproject.toml``
* Make sure you've `set up your PyPI credential`_ with poetry
* Then run:

.. _set up your PyPI credential: https://python-poetry.org/docs/repositories/#configuring-credentials

.. code-block:: console

    towncrier build --draft  # verify this works then run
    towncrier build
    poetry build
    poetry publish --dry-run  # verify this succeeds
    poetry publish
