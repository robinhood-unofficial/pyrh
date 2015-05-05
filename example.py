from Robinhood import Robinhood
import keyring;

my_trader = Robinhood(username=keyring.get_password("system", "usernameRobinhood"), password=keyring.get_password("system", "passwordRobinhood"));

#get stock information about a stock
# Note: for some stock names, more than one instrument
#       may be returned for a given stock symbol
stock_instrument = my_trader.instruments("GEVO")[0]

print(stock_instrument)

#You can stock information about current bid_price, etc
quote_info = my_trader.quote_data("GEVO")

#place a buy order (uses market bid price)
#buy_order = my_trader.place_buy_order(stock_instrument, 1)

#place a sell order
#sell_order = my_trader.place_sell_order(stock_instrument, 1)


