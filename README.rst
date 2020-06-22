.. image:: https://i.imgur.com/74CYw5g.png
   :target: https://github.com/robinhood-unofficial/pyrh
   :alt: robinhood-logo

-------------------------------------------------------------

pyrh - Unofficial Robinhood API
###############################

.. image:: https://github.com/robinhood-unofficial/pyrh/workflows/build/badge.svg?branch=master&event=push
   :target: https://github.com/robinhood-unofficial/pyrh/actions?query=workflow%3Abuild+branch%3Amaster
   :alt: Build Status

.. image:: https://codecov.io/gh/robinhood-unofficial/pyrh/branch/master/graph/badge.svg
   :target: https://codecov.io/gh/robinhood-unofficial/pyrh
   :alt: Coverage

.. image:: https://readthedocs.org/projects/pyrh/badge/?version=latest
   :target: https://pyrh.readthedocs.io/en/latest/?badge=latest
   :alt: Documentation Status

.. image:: https://img.shields.io/pypi/v/pyrh?style=plastic
   :target: https://pypi.org/project/pyrh/
   :alt: PyPI Version

.. image:: https://img.shields.io/pypi/dm/pyrh?color=blue&style=plastic
   :target: https://pypi.org/project/pyrh/
   :alt: PyPI - Downloads

.. image:: https://img.shields.io/github/license/robinhood-unofficial/Robinhood
   :target: https://github.com/robinhood-unofficial/pyrh/blob/master/LICENSE
   :alt: License

.. image:: https://img.shields.io/badge/code%20style-black-000000.svg
   :target: https://github.com/psf/black
   :alt: Code Style

.. image:: https://img.shields.io/gitter/room/J-Robinhood/Lobby
   :target: https://gitter.im/J-Robinhood/Lobby?utm_source=badge&utm_medium=badge&utm_campaign=pr-badge&utm_content=badge
   :alt: Gitter

Python Framework to make trades with Unofficial Robinhood API. Supports Python 3.6+

*Please note that parts of this project maybe non-functional / under rapid development*
#######################################################################################

* A stable release is imminent

Documentation: https://pyrh.readthedocs.io/en/latest/

Quick start
***********

.. code-block:: python

   from pyrh import Robinhood

   rh = Robinhood()
   rh.login(username="YOUR_EMAIL", password="YOUR_PASSWORD")
   rh.print_quote("AAPL")

How To Install:
***************

.. code-block::

   pip install pyrh

Running example.ipynb_
**********************

.. _example.ipynb: https://github.com/robinhood-unofficial/pyrh/blob/master/notebooks/example.ipynb

Clone the repository and install jupyter capabilities.

.. code-block::

   $ git clone https://github.com/robinhood-unofficial/pyrh.git
   $ cd pyrh
   $ python --version # python 3.3+ for venv functionality
   Python 3.7.6
   $ python -m venv pyrh_env
   $ source pyrh_env/bin/activate
   (pyrh_env) $ pip install .[notebook]
   (pyrh_env) $ cp .env.sample .env # update the values in here
   (pyrh_env) $ jupyter notebook notebooks/example.ipynb

Now just run the files in the example.

Related
*******

* `robinhood-ruby <https://github.com/rememberlenny/robinhood-ruby>`_ - RubyGem for interacting with Robinhood API
* `robinhood-node <https://github.com/aurbano/robinhood-node>`_ - NodeJS module to make trades with Robinhood Private API
* See the original `blog post <https://medium.com/@rohanpai25/reversing-robinhood-free-accessible-automated-stock-trading-f40fba1e7d8b>`_.
