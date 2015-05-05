# Robinhood
Python Framework to make trades with Robinhood Private API
See Blog Post: https://medium.com/@rohanpai25/reversing-robinhood-free-accessible-automated-stock-trading-f40fba1e7d8b

Current Features Include:
- Placing buy orders (Robinhood.place_buy_order)
- Placing sell order (Robinhood.place_sell_order)
- Quote Information (Robinhood.quote_data)
- More coming soon

How To Install:

    >pip install -r requirements.txt

How to Use (see example.py):

    from Robinhood import Robinhood
    my_trader = Robinhood(username="USERNAME HERE", password="PASSWORD HERE")
    stock_instrument = my_trader.instruments("GEVO")[0]
    quote_info = my_trader.quote_data("GEVO")
    buy_order = my_trader.place_buy_order(stock_instrument, 1)
    sell_order = my_trader.place_sell_order(stock_instrument, 1)

One way to store your login information (see example.py)
[Python's Keyring Library](https://pypi.python.org/pypi/keyring#using-keyring)
Usage:
    import keyring;

    #Create temporary credntial.py with this information, run it, and then securely delete it
    keyring.set_password("system", "usernameRobinhood", "your_user_name");
    keyring.set_password("system", "passwordRobinhood", "your_password");

    #Create a new trader with your stored username/password
    my_trader = Robinhood(keyring.get_password("system", "usernameRobinhood"), keyring.get_password("system", "passwordRobinhood"));
