# Robinhood

WARNING!!

This API is no longer suitable for fully-autonomous trading strategies.
Robinhood has required a 2FA.
This API can be run from the console, where the user will have to input an SMS code sent to their phone.
After logging in, the SMS code expires after 24 hours.
In theory, one could trade with an algorithm if they signed in with the console at the beginning of the trading day.

[![Join the chat at https://gitter.im/J-Robinhood/Lobby](https://badges.gitter.im/J-Robinhood/Lobby.svg)](https://gitter.im/J-Robinhood/Lobby?utm_source=badge&utm_medium=badge&utm_campaign=pr-badge&utm_content=badge)
Python Framework to make trades with Robinhood Private API.
See this [blog post](https://medium.com/@rohanpai25/reversing-robinhood-free-accessible-automated-stock-trading-f40fba1e7d8b).

## Current Features 
- Placing buy orders (`Robinhood.place_market_buy_order` and `Robinhood.place_limit_buy_order`)
- Placing sell order (`Robinhood.place_market_sell_order` and `Robinhood.place_limit_sell_order`)
- Fetch and cancel orders (`Robinhood.order_history` and `Robinhood.cancel_order`)
- Quote information (`Robinhood.quote_data`)
- User portfolio data (`Robinhood.portfolios`)
- User positions data (`Robinhood.positions`)
- More coming soon

### How To Install:
    pip install .
    
### Converting to Python 3
Project will work on both python 2 and python 3

### How to Use (see [example.py](https://github.com/Jamonek/Robinhood/blob/master/docs/example.py))

    from Robinhood import Robinhood
    my_trader = Robinhood()
    logged_in = my_trader.login(username="USERNAME HERE", password="PASSWORD HERE")
    stock_instrument = my_trader.instruments("GEVO")[0]
    quote_info = my_trader.quote_data("GEVO")
    buy_order = my_trader.place_market_buy_order(stock_instrument["url], "GEVO", "GFD", 1)
    sell_order = my_trader.place_market_sell_order(stock_instrument["url"], "GEVO", "GFD", 1)

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

# Related

* [robinhood-ruby](https://github.com/rememberlenny/robinhood-ruby) - RubyGem for interacting with Robinhood API
* [robinhood-node](https://github.com/aurbano/robinhood-node) - NodeJS module to make trades with Robinhood Private API
