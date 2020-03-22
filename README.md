[![robinhood-logo](logo.png)](https://github.com/robinhood-unofficial/Robinhood)
------------

# pyrh - Unofficial Robinhood API

[![Gitter](https://img.shields.io/gitter/room/J-Robinhood/Lobby)](https://gitter.im/J-Robinhood/Lobby?utm_source=badge&utm_medium=badge&utm_campaign=pr-badge&utm_content=badge)
[![GitHub](https://img.shields.io/github/license/robinhood-unofficial/Robinhood)](https://github.com/robinhood-unofficial/Robinhood/blob/master/LICENSE)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

Python Framework to make trades with Unofficial Robinhood API. Supports Python 3.6+

## Current Features
- Placing buy orders (`Robinhood.place_buy_order`)
- Placing sell order (`Robinhood.place_sell_order`)
- Fetch and cancel orders (`Robinhood.order_history` and `Robinhood.cancel_order`)
- Quote information (`Robinhood.quote_data`)
- User portfolio data (`Robinhood.portfolios`)
- User positions data (`Robinhood.positions`)
- More coming soon

### How To Install:

```
pip install pyrh
```

### Running [example.ipynb](https://github.com/robinhood-unofficial/Robinhood/blob/master/notebooks/example.ipynb)
* Install jupyter
```
$ python --version # python 3.3+ for venv functionality
Python 3.7.6
$ python -m venv pyrh_env
$ source pyrh_env/bin/activate
(pyrh_env) $ pip install pyrh
(pyrh_env) $ pip install jupyter
(pyrh_env) $ jupyter notebook
```

Then navigate to the example file linked above and run it.

### Data returned
* Quote data
  + Ask Price
  + Ask Size
  + Bid Price
  + Bid Size
  + Last trade price
  + Previous close
  + Previous close date
  + Adjusted previous close
  + Trading halted
  + Updated at
  + Historical Price
* User portfolio data
  + Adjusted equity previous close
  + Equity
  + Equity previous close
  + Excess margin
  + Extended hours equity
  + Extended hours market value
  + Last core equity
  + Last core market value
  + Market value
  + Order history
  + Dividend history
* User positions data
  + Securities owned
* News

------------------

# Changelog
## 2.0
* Fixed 2fa connection issues
* Last version to support python 2

## 1.0.1
* Added custom exception

# Developer setup
* Python 3.7+ is required
* poetry is used to manage package dependencies
* pre-commit is used to manage the project's tooling and linting
  * black
  * flake8
```
brew install poetry
brew install pre-commit
poetry install
pre-commit install
```

Lint checks are automatically run when you try to push the code. To manually run them
run the following command.
```
pre-commit run -a
```

# Related
* [robinhood-ruby](https://github.com/rememberlenny/robinhood-ruby) - RubyGem for interacting with Robinhood API
* [robinhood-node](https://github.com/aurbano/robinhood-node) - NodeJS module to make trades with Robinhood Private API
* See the original [blog post](https://medium.com/@rohanpai25/reversing-robinhood-free-accessible-automated-stock-trading-f40fba1e7d8b).
