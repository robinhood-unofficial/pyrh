from Robinhood import Robinhood
import json
from pprint import pprint

with open('.credentials.json') as data_file:
    credentials = json.load(data_file)

#Setup
my_trader = Robinhood()
#login
my_trader.login(username=credentials["username"], password=credentials["password"])

pprint(my_trader.get_options('AAPL', ['2018-10-12'], 'put'))
pprint(my_trader.get_option_market_data('7d717c0e-cb8c-44ce-adad-332fe90e1753'))

#Get stock information
    #Note: Sometimes more than one instrument may be returned for a given stock symbol
# stock_instrument = my_trader.instruments("GEVO")[0]
#
# #Get a stock's quote
# my_trader.print_quote("AAPL")
#
# #Prompt for a symbol
# my_trader.print_quote()
#
# #Print multiple symbols
# my_trader.print_quotes(stocks=["BBRY", "FB", "MSFT"])
#
# #View all data for a given stock ie. Ask price and size, bid price and size, previous close, adjusted previous close, etc.
# quote_info = my_trader.quote_data("GEVO")
# print(quote_info)
#
# #Place a buy order (uses market bid price)
# buy_order = my_trader.place_buy_order(stock_instrument, 1)
#
# #Place a sell order
# sell_order = my_trader.place_sell_order(stock_instrument, 1)
