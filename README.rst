.. image:: https://i.imgur.com/74CYw5g.png
   :target: https://github.com/robinhood-unofficial/pyrh
   :alt: robinhood-logo

-------------------------------------------------------------

pyrh - Unofficial Robinhood API
###############################

.. image:: https://github.com/robinhood-unofficial/pyrh/workflows/build/badge.svg?branch=master&event=push
   :target: https://github.com/robinhood-unofficial/pyrh/actions?query=workflow%3Abuild+branch%3Amaster
   :alt: build

.. image:: https://img.shields.io/pypi/dm/pyrh?color=blue&style=plastic
   :target: https://pypi.org/project/pyrh/
   :alt: PyPI - Downloads

.. image:: https://img.shields.io/github/license/robinhood-unofficial/Robinhood
   :target: https://github.com/robinhood-unofficial/pyrh/blob/master/LICENSE
   :alt: GitHub

.. image:: https://img.shields.io/badge/code%20style-black-000000.svg
   :target: https://github.com/psf/black
   :alt: Code style: black

.. image:: https://img.shields.io/gitter/room/J-Robinhood/Lobby
   :target: https://gitter.im/J-Robinhood/Lobby?utm_source=badge&utm_medium=badge&utm_campaign=pr-badge&utm_content=badge
   :alt: Gitter

Python Framework to make trades with Unofficial Robinhood API. Supports Python 3.6+

*Please note that parts of this project maybe non-functional / under rapid development*
#######################################################################################

* A stable release is iminent

Quickstart
**********

.. code-block:: python

   from pyrh import Robinhood

   rh = Robinhood()
   rh.login(username="YOUR_EMAIL", password="YOUR_PASSWORD")
   rh.print_quote("AAPL")

How To Install:
***************

.. code-block::

   pip install pyrh

Current Features
****************

* Placing buy orders (\ ``Robinhood.place_buy_order``\ )
* Placing sell order (\ ``Robinhood.place_sell_order``\ )
* Fetch and cancel orders (\ ``Robinhood.order_history`` and ``Robinhood.cancel_order``\ )
* Quote information (\ ``Robinhood.quote_data``\ )
* User portfolio data (\ ``Robinhood.portfolio``\ )
* User positions data (\ ``Robinhood.positions``\ )
* More coming soon

Running example.ipynb_
**********************

.. _example.ipynb: https://github.com/robinhood-unofficial/pyrh/blob/master/notebooks/example.ipynb

* Install jupyter
  .. code-block::

     $ python --version # python 3.3+ for venv functionality
     Python 3.7.6
     $ python -m venv pyrh_env
     $ source pyrh_env/bin/activate
     (pyrh_env) $ pip install pyrh
     (pyrh_env) $ pip install jupyter
     (pyrh_env) $ jupyter notebook

Then navigate to the example file linked above and run it.

Data returned
*************
* Quote data

  * Ask Price
  * Ask Size
  * Bid Price
  * Bid Size
  * Last trade price
  * Previous close
  * Previous close date
  * Adjusted previous close
  * Trading halted
  * Updated at
  * Historical Price

* User portfolio data

  * Adjusted equity previous close
  * Equity
  * Equity previous close
  * Excess margin
  * Extended hours equity
  * Extended hours market value
  * Last core equity
  * Last core market value
  * Market value
  * Order history
  * Dividend history

* User positions data

  * Securities owned

* News

Related
*******

* `robinhood-ruby <https://github.com/rememberlenny/robinhood-ruby>`_ - RubyGem for interacting with Robinhood API
* `robinhood-node <https://github.com/aurbano/robinhood-node>`_ - NodeJS module to make trades with Robinhood Private API
* See the original `blog post <https://medium.com/@rohanpai25/reversing-robinhood-free-accessible-automated-stock-trading-f40fba1e7d8b>`_.
