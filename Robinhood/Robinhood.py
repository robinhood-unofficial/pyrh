"""Robinhood.py: a collection of utilities for working with Robinhood's Private API"""
import getpass
import logging
import warnings
from enum import Enum

import requests
import six
from six.moves.urllib.parse import unquote
from six.moves.urllib.request import getproxies
from six.moves import input
from . import exceptions as RH_exception

class Bounds(Enum):
    """enum for bounds in `historicals` endpoint"""
    REGULAR = 'regular'
    EXTENDED = 'extended'

class Transaction(Enum):
    """enum for buy/sell orders"""
    BUY = 'buy'
    SELL = 'sell'

class Trigger(Enum):
    """enum for buy/sell orders"""
    IMMEDIATE = 'immediate'
    STOP = 'stop'

class Order(Enum):
    """enum for buy/sell orders"""
    MARKET = 'market'
    LIMIT = 'limit'

class TimeForce(Enum):
    """enum for buy/sell orders"""
    GTC = 'gtc'
    GFD = 'gfd'
    IOC = 'ioc'
    FOK = 'fok'
    OPG = 'opg'

class OrderState(Enum):
    """enum for order states"""
    QUEUED = "queued"
    UNCONFIRMED = "unconfirmed"
    CONFIRMED = "confirmed"
    PARTIALLY_FILLED = "partially_filled"
    FILLED = "filled"
    REJECTED = "rejected"
    CANCELLED = "cancelled"
    FAILED = "failed"

class Robinhood:
    """wrapper class for fetching/parsing Robinhood endpoints"""
    endpoints = {
        "login": "https://api.robinhood.com/api-token-auth/",
        "logout": "https://api.robinhood.com/api-token-logout/",
        "investment_profile": "https://api.robinhood.com/user/investment_profile/",
        "accounts": "https://api.robinhood.com/accounts/",
        "ach_iav_auth": "https://api.robinhood.com/ach/iav/auth/",
        "ach_relationships": "https://api.robinhood.com/ach/relationships/",
        "ach_transfers": "https://api.robinhood.com/ach/transfers/",
        "applications": "https://api.robinhood.com/applications/",
        "dividends": "https://api.robinhood.com/dividends/",
        "edocuments": "https://api.robinhood.com/documents/",
        "instruments": "https://api.robinhood.com/instruments/",
        "instrumentid": "https://api.robinhood.com/instruments/{instrumentid}/",
        "instrumentsplits": "https://api.robinhood.com/instruments/{instrumentid}/splits/",
        "margin_upgrades": "https://api.robinhood.com/margin/upgrades/",
        "markets": "https://api.robinhood.com/markets/",
        "notifications": "https://api.robinhood.com/notifications/",
        "orders": "https://api.robinhood.com/orders/",
        "cancel": "https://api.robinhood.com/orders/{oid}/cancel/",
        "password_reset": "https://api.robinhood.com/password_reset/request/",
        "portfolios": "https://api.robinhood.com/portfolios/",
        "positions": "https://api.robinhood.com/positions/",
        "quotes": "https://api.robinhood.com/quotes/",
        "historicals": "https://api.robinhood.com/quotes/historicals/",
        "document_requests": "https://api.robinhood.com/upload/document_requests/",
        "user": "https://api.robinhood.com/user/",
        "watchlists": "https://api.robinhood.com/watchlists/",
        "news": "https://api.robinhood.com/midlands/news/",
        "fundamentals": "https://api.robinhood.com/fundamentals/",
    }

    session = None

    username = None

    password = None

    headers = None

    auth_token = None

    logger = logging.getLogger('Robinhood')
    logger.addHandler(logging.NullHandler())

    ##############################
    #Logging in and initializing
    ##############################

    def __init__(self):
        self.session = requests.session()
        self.session.proxies = getproxies()
        self.headers = {
            "Accept": "*/*",
            "Accept-Encoding": "gzip, deflate",
            "Accept-Language": "en;q=1, fr;q=0.9, de;q=0.8, ja;q=0.7, nl;q=0.6, it;q=0.5",
            "Content-Type": "application/x-www-form-urlencoded; charset=utf-8",
            "X-Robinhood-API-Version": "1.0.0",
            "Connection": "keep-alive",
            "User-Agent": "Robinhood/823 (iPhone; iOS 7.1.2; Scale/2.00)"
        }
        self.session.headers = self.headers

    def login_prompt(self): #pragma: no cover
        """Prompts user for username and password and calls login()."""
        username = input("Username: ")
        password = getpass.getpass()
        return self.login(username=username, password=password)

    def login(
            self,
            username,
            password,
            mfa_code=None
        ):
        """save and test login info for Robinhood accounts

        Args:
            username (str): username
            password (str): password

        Returns:
            (bool): received valid auth token

        """
        self.username = username
        self.password = password
        payload = {
            'password': self.password,
            'username': self.username
        }

        if mfa_code:
            payload['mfa_code'] = mfa_code

        try:
            res = self.session.post(
                self.endpoints['login'],
                data=payload
            )
            res.raise_for_status()
            data = res.json()
        except requests.exceptions.HTTPError:
            raise RH_exception.LoginFailed()

        if 'mfa_required' in data.keys():           #pragma: no cover
            raise RH_exception.TwoFactorRequired()  #requires a second call to enable 2FA

        if 'token' in data.keys():
            self.auth_token = data['token']
            self.headers['Authorization'] = 'Token ' + self.auth_token
            return True

        return False

    def logout(self):
        """logout from Robinhood

        Returns:
            (:obj:`requests.request`) result from logout endpoint

        """
        try:
            res = self.session.post(self.endpoints['logout'])
            res.raise_for_status()
        except requests.exceptions.HTTPError as err_msg:
            warnings.warn('Failed to log out ' + repr(err_msg))

        self.headers['Authorization'] = None
        self.auth_token = None

        return res

    ##############################
    #GET DATA
    ##############################

    def investment_profile(self):
        """fetch investment_profile"""
        res = self.session.get(self.endpoints['investment_profile'])
        res.raise_for_status()  #will throw without auth
        data = res.json()
        return data

    def instruments(self, query=None, symbol=None, instrumentid=None):
        """fetch instruments endpoint

        Args:
            query (str): search for ticker, e.g. by company name
            symbol (str): find instrument by it's symbol
            instrumentid (str): instrumentid [uuid without the rest of URL]

        Returns:
            (:obj:`dict`): JSON contents from `instruments` endpoint

        """
        res = None
        if instrumentid:
            res = self.session.get(
                self.endpoints['instrumentid'].format(instrumentid=instrumentid)
            )
        else:
            params = {}
            if symbol:
                params['symbol'] = symbol.upper()
            if query:
                params['query'] = query
            res = self.session.get(
                self.endpoints['instruments'],
                params=params
            )
        res.raise_for_status()
        res = res.json()

        # if requesting all, return entire object so may paginate with ['next']
        # Not sure variable returns types here is the best approach..
        # API doesn't return pagination though when query is non-empty query=a ??
        #if query is None and not (symbol or instrumentid):
        #     return res
        # XXX perhaps should return an iterable to hide the pagination, e.g. res['next'], res['previous'] aspects
        return res['results']

    def instrument_splits(self, instrumentid=None):
        """fetch instruments splits endpoint

        Args:
            instrumentid (str): instrumentid [uuid without the rest of URL]

        Returns:
            (:obj:`dict`): JSON contents from `instruments splits` endpoint

        """
        res = None
        if instrumentid:
            res = self.session.get(
                self.endpoints['instrumentsplits'].format(instrumentid=instrumentid)
            )
        res.raise_for_status()
        return res.json()

    def quote_data(self, stock):
        """fetch stock quote

        Args:
            stock (list|str): stock ticker, prompt if blank

        Returns:
            (:obj:`dict`): JSON contents from `quotes` endpoint

        """
        url = None
        stocks = None
        if isinstance(stock,str):
            stocks = stock
        elif isinstance(stock,list):
            stocks = ','.join(stock)

        #if stock.find(',') == -1:
        #    url = str(self.endpoints['quotes']) + str(stock) + "/"
        url = str(self.endpoints['quotes']) + "?symbols=" + str(stocks)
        #Check for validity of symbol

        try:
            res = requests.get(url)
            res.raise_for_status()
        except requests.exceptions.HTTPError:
            raise NameError('Invalid Symbol: ' + stocks) #TODO: custom exception

        return res.json()

    # We will keep for compatibility until next major release
    def quotes_data(self, stocks):
        """Fetch quote for multiple stocks, in one single Robinhood API call

        Args:
            stocks (list<str>): stock tickers

        Returns:
            (:obj:`list` of :obj:`dict`): List of JSON contents from `quotes` endpoint, in the
            same order of input args. If any ticker is invalid, a None will occur at that position.
        """
        url = str(self.endpoints['quotes']) + "?symbols=" + ",".join(stocks)
        try:
            res = requests.get(url)
            res.raise_for_status()
        except requests.exceptions.HTTPError:
            raise NameError('Invalid Symbols: ' + ",".join(stocks)) #TODO: custom exception

        return res.json()["results"]

    def get_quote_list(self, stock='', key=''):
        """Returns multiple stock info and keys from quote_data (prompt if blank)

        Args:
            stock (str): stock ticker (or tickers separated by a comma)
            , prompt if blank
            key (str): key attributes that the function should return

        Returns:
            (:obj:`list`): Returns values from each stock or empty list
                           if none of the stocks were valid

        """
        #Creates a tuple containing the information we want to retrieve
        def append_stock(stock):
            keys = key.split(',')
            myStr = ''
            for item in keys:
                myStr += stock[item] + ","
            return (myStr.split(','))

        #Prompt for stock if not entered
        if not stock:   #pragma: no cover
            stock = input("Symbol: ")
        data = self.quote_data(stock)

        res = []
        # Handles the case of multple tickers
        if stock.find(',') != -1:
            for stock in data['results']:
                if stock == None:
                    continue
                res.append(append_stock(stock))
        else:
            res.append(append_stock(data))
        return res

    def get_quote(self, stock=''):
        """wrapper for quote_data"""
        data = self.quote_data(stock)
        return data["symbol"]

    def get_quote_fields(self, stocks=None, fields=None):
        """Returns multiple stock info and fields from quote_data

        Args:
            stock (str|array): stock ticker(s) (or tickers separated by a comma), prompt if blank
            key (str): key attributes that the function should return

        Returns:
            (:obj:`list`): Returns values from each stock or empty list
                           if none of the stocks were valid

        """
        data = self.quote_data(stocks)

        if fields is not None and 'symbol' not in fields:
            fields.append('symbol')

        res = {}
        for quote in data['results']:
            if not isinstance(quote,dict):
                raise Warning("Returned Quote was not a dict")

            # XXX what if symbol is non-unique should we use symbol as key here?
            s = quote['symbol']
            if fields is None:
                res[s] = quote
            else:
                res[s] = {key: value for (key, value) in quote.items() if key in fields}
        return res

    def get_historical_quotes(
            self,
            stock,
            interval,
            span,
            bounds=Bounds.REGULAR
        ):
        """fetch historical data for stock

        Note: valid interval/span configs
            interval = 5minute | 10minute + span = day, week
            interval = day + span = year
            interval = week
            TODO: NEEDS TESTS

        Args:
            stock (str): stock ticker
            interval (str): resolution of data
            span (str): length of data
            bounds (:enum:`Bounds`, optional): 'extended' or 'regular' trading hours

        Returns:
            (:obj:`dict`) values returned from `historicals` endpoint

        """
        if isinstance(bounds, str): #recast to Enum
            bounds = Bounds(bounds)

        params = {
            'symbols': ','.join(stock).upper(),
            'interval': interval,
            'span': span,
            'bounds': bounds.name.lower()
        }
        res = self.session.get(
            self.endpoints['historicals'],
            params=params
        )
        res.raise_for_status()
        return res.json()

    def get_news(self, stock):
        """fetch news endpoint
        Args:
            stock (str): stock ticker

        Returns:
            (:obj:`dict`) values returned from `news` endpoint

        """
        res = self.session.get(self.endpoints['news']+stock.upper()+"/")
        res.raise_for_status()
        return res.json()

    def print_quote(self, stock):    #pragma: no cover
        """print quote information
        Args:
            stock (:obj:`list`): list of symbols to fetch and print quotes

        Returns:
            None

        """
        data = self.get_quote_list(stock,('symbol','last_trade_price'))
        for item in data:
            quote_str = item[0] + ": $" + item[1]
            print(quote_str)
            self.logger.info(quote_str)

    def print_quotes(self, stocks): #pragma: no cover
        """print a collection of stocks

        Args:
            stocks (:obj:`list`): list of stocks to pirnt

        Returns:
            None

        """
        self.print_quote(stock)

    def ask_price(self, stock=''):
        """get asking price for a stock

        Note:
            queries `quote` endpoint, dict wrapper

        Args:
            stock (str): stock ticker

        Returns:
            (float): ask price

        """
        return self.get_quote_list(stock,'ask_price')

    def ask_size(self, stock=''):
        """get ask size for a stock

        Note:
            queries `quote` endpoint, dict wrapper

        Args:
            stock (str): stock ticker

        Returns:
            (int): ask size

        """
        return self.get_quote_list(stock,'ask_size')

    def bid_price(self, stock=''):
        """get bid price for a stock

        Note:
            queries `quote` endpoint, dict wrapper

        Args:
            stock (str): stock ticker

        Returns:
            (float): bid price

        """
        return self.get_quote_list(stock,'bid_price')

    def bid_size(self, stock=''):
        """get bid size for a stock

        Note:
            queries `quote` endpoint, dict wrapper

        Args:
            stock (str): stock ticker

        Returns:
            (int): bid size

        """
        return self.get_quote_list(stock,'bid_size')

    def last_trade_price(self, stock=''):
        """get last trade price for a stock

        Note:
            queries `quote` endpoint, dict wrapper

        Args:
            stock (str): stock ticker

        Returns:
            (float): last trade price

        """
        return self.get_quote_list(stock,'last_trade_price')

    def previous_close(self, stock=''):
        """get previous closing price for a stock

        Note:
            queries `quote` endpoint, dict wrapper

        Args:
            stock (str): stock ticker

        Returns:
            (float): previous closing price

        """
        return self.get_quote_list(stock,'previous_close')

    def previous_close_date(self, stock=''):
        """get previous closing date for a stock

        Note:
            queries `quote` endpoint, dict wrapper

        Args:
            stock (str): stock ticker

        Returns:
            (str): previous close date

        """
        return self.get_quote_list(stock,'previous_close_date')

    def adjusted_previous_close(self, stock=''):
        """get adjusted previous closing price for a stock

        Note:
            queries `quote` endpoint, dict wrapper

        Args:
            stock (str): stock ticker

        Returns:
            (float): adjusted previous closing price

        """
        return self.get_quote_list(stock,'adjusted_previous_close')

    def symbol(self, stock=''):
        """get symbol for a stock

        Note:
            queries `quote` endpoint, dict wrapper

        Args:
            stock (str): stock ticker

        Returns:
            (str): stock symbol

        """
        return self.get_quote_list(stock,'symbol')

    def last_updated_at(self, stock=''):
        """get last update datetime

        Note:
            queries `quote` endpoint, dict wrapper

        Args:
            stock (str): stock ticker

        Returns:
            (str): last update datetime

        """
        return self.get_quote_list(stock,'last_updated_at')
        #TODO: recast to datetime object?

    def get_account(self):
        """fetch account information

        Returns:
            (:obj:`dict`): `accounts` endpoint payload

        """
        res = self.session.get(self.endpoints['accounts'])
        res.raise_for_status()  #auth required
        res = res.json()
        return res['results'][0]

    def get_url(self, url):
        """flat wrapper for fetching URL directly"""
        return self.session.get(url).json()

    ##############################
    #GET FUNDAMENTALS
    ##############################

    def get_fundamentals(self, stock=''):
        """find stock fundamentals data

        Args:
            (str): stock ticker

        Returns:
            (:obj:`dict`): contents of `fundamentals` endpoint

        """
        #Prompt for stock if not entered
        if not stock:   #pragma: no cover
            stock = input("Symbol: ")

        url = str(self.endpoints['fundamentals']) + str(stock.upper()) + "/"
        # XXX endpoint also acccepts POST 'symbols=STOCK1,STOCK2' CSV list of 10 symbols
        #Check for validity of symbol
        res = None
        try:
            res = requests.get(url)
            res.raise_for_status()
        except requests.exceptions.HTTPError:
            raise NameError('Invalid Symbol: ' + stock) #TODO wrap custom exception

        return res.json()

    def fundamentals(self, stock=''):
        """wrapper for get_fundamentlals function"""
        return self.get_fundamentals(stock)

    ##############################
    # PORTFOLIOS DATA
    ##############################

    def portfolios(self):
        """Returns the user's portfolio data."""
        res = self.session.get(self.endpoints['portfolios'])
        res.raise_for_status()
        return res.json()['results'][0]

    def adjusted_equity_previous_close(self):
        """wrapper for portfolios

        get `adjusted_equity_previous_close` value

        """
        return float(self.portfolios()['adjusted_equity_previous_close'])

    def equity(self):
        """wrapper for portfolios

        get `equity` value

        """
        return float(self.portfolios()['equity'])

    def equity_previous_close(self):
        """wrapper for portfolios

        get `equity_previous_close` value

        """
        return float(self.portfolios()['equity_previous_close'])

    def excess_margin(self):
        """wrapper for portfolios

        get `excess_margin` value

        """
        return float(self.portfolios()['excess_margin'])

    def extended_hours_equity(self):
        """wrapper for portfolios

        get `extended_hours_equity` value

        """
        try:
            return float(self.portfolios()['extended_hours_equity'])
        except TypeError:
            return None

    def extended_hours_market_value(self):
        """wrapper for portfolios

        get `extended_hours_market_value` value

        """
        try:
            return float(self.portfolios()['extended_hours_market_value'])
        except TypeError:
            return None

    def last_core_equity(self):
        """wrapper for portfolios

        get `last_core_equity` value

        """
        return float(self.portfolios()['last_core_equity'])

    def last_core_market_value(self):
        """wrapper for portfolios

        get `last_core_market_value` value

        """
        return float(self.portfolios()['last_core_market_value'])

    def market_value(self):
        """wrapper for portfolios

        get `market_value` value

        """
        return float(self.portfolios()['market_value'])

    def order_history(self,instrument=None):
        """

        get orders from account

        Args:
            instrument (string): RH instrument URL to restrict results
        """
        data = {}
        # API Documentation question:
        # state or updated_at did not appear to filter the order details,
        # while this would seem useful over time,  it is not clear if this
        # truly exists in the RH API.
        # Will be nice when RH officially supports and documents a public API :)
        # if state is not None:
        #     data['state'] = state
        #
        # if since is not None:
        #     data['updated_at'] = since
        if instrument is not None:
            data['instrument'] = instrument
        res = self.session.get(self.endpoints['orders'], params=data)
        res.raise_for_status()
        return res.json()

    def dividends(self):
        """wrapper for portfolios

        get dividends from account

        """
        return self.session.get(self.endpoints['dividends']).json()

    ##############################
    # POSITIONS DATA
    ##############################

    def positions(self):
        """Returns the user's positions data."""
        return self.session.get(self.endpoints['positions']).json()

    def securities_owned(self):
        """
        Returns a list of symbols of securities of which there are more
        than zero shares in user's portfolio.
        """
        return self.session.get(self.endpoints['positions']+'?nonzero=true').json()

    ##############################
    #PLACE ORDER
    ##############################

    def place_order(
            self,
            instrument,
            quantity,
            transaction,
            bid_price=None,
            stop_price=None,
            trigger=Trigger('immediate'),
            order=Order('market'),
            time_in_force = TimeForce('gfd')
        ):
        """place an order with Robinhood

        Notes:
            OMFG TEST THIS PLEASE!

            Just realized this won't work since if type is LIMIT you need to use "price" and if
            a STOP you need to use "stop_price".  Oops.
            Reference: https://github.com/sanko/Robinhood/blob/master/Order.md#place-an-order

        Args:
            instrument (dict): the RH URL and symbol in dict for the instrument to be traded
            quantity (int): quantity of stocks in order
            bid_price (float): price for order
            stop_price (float): price at which order is placed
            transaction (:enum:`Transaction`): BUY or SELL enum
            trigger (:enum:`Trigger`): IMMEDIATE or STOP enum
            order (:enum:`Order`): MARKET or LIMIT emum
            time_in_force (:enum:`TIME_IN_FORCE`): GFD or GTC (Good for day or Good 'til Cancelled)

        Returns:
            (:obj:`requests.request`): result from `orders` put command

        """

        if isinstance(transaction, str):
            transaction = Transaction(transaction.lower())
        if isinstance(trigger, str):
            trigger = Trigger(trigger.lower())
        if isinstance(order, str):
            order = Order(order.lower())
        if isinstance(time_in_force,str):
            time_in_force = TimeForce(time_in_force.lower())

        # NOT SURE why bid_price is being assumed here, this could be bad.

        if order == Order.LIMIT and bid_price is None:
            raise ValueError("Order.LIMIT without bid_price")

        if bid_price is not None and not order == Order.LIMIT:
            raise ValueError("bid_price without Order.LIMIT")

        # If Order.MARKET the we still need to pass RH a price, RH places market orders
        # automatically as limit orders with a 5% buffer
        if not bid_price and order == Order.MARKET:
            bid_price = self.quote_data(instrument['symbol'])['bid_price']

        payload = {
            'account': self.get_account()['url'],
            'instrument': unquote(instrument['url']),
            'quantity': int(quantity),
            'price': float(bid_price),

            'side': transaction.value,
            'symbol': instrument['symbol'],
            'time_in_force': time_in_force.value,
            'trigger': trigger.value,
            'type': order.value
        }

        if trigger == Trigger.STOP:
            if stop_price is not None:
                payload['stop_price'] = float(stop_price)
            else:
                raise ValueError("Trigger.STOP without stop_price")
        elif stop_price is not None:
            raise ValueError("stop_price without Trigger.STOP")

        # res = payload
        res = self.session.post(
            self.endpoints['orders'],
            data=payload
        )
        res.raise_for_status()
        return res

    def place_buy_order(
            self,
            instrument,
            quantity,
            bid_price=0.0
    ):
        """wrapper for placing buy orders

        Args:
            instrument (dict): the RH URL and symbol in dict for the instrument to be traded
            quantity (int): quantity of stocks in order
            bid_price (float): price for order

        Returns:
            (:obj:`requests.request`): result from `orders` post command

        """
        transaction = Transaction.BUY
        return self.place_order(instrument, quantity, bid_price, transaction)

    def place_sell_order(
            self,
            instrument,
            quantity,
            bid_price=0.0
    ):
        """wrapper for placing sell orders

        Args:
            instrument (dict): the RH URL and symbol in dict for the instrument to be traded
            quantity (int): quantity of stocks in order
            bid_price (float): price for order

        Returns:
            (:obj:`requests.request`): result from `orders` put command

        """
        transaction = Transaction.SELL
        return self.place_order(instrument, quantity, bid_price, transaction)

    ##############################
    # CANCEL ORDER
    ##############################
    def cancel_order(self,oid):
        """
        cancel a given order id

        Args:
            oid (string): the order ID to be cancelled
        Returns:
            (:obj:`requests.request`): result from `orders` put command
            status code 200 signifies success

        """
        data = {}
        data['oid'] = oid
        res = self.session.post(self.endpoints['cancel'].format(**data))
        res.raise_for_status()
        return res


    def cancel_orders_all(self,instrument=None):
        """
        convenience function to cancel all orders, optionally only for a given instrument

        Args:
            instrument (string): RH instrument URL to restrict results
        Returns:
            (:obj:`dict`): containing keys 'cancelled' or 'error' with the list of order ids
        """
        orders = self.order_history(instrument=instrument)
        res = {'cancelled':[], 'error':[]}
        stoppedOrderStates = (OrderState.FILLED, OrderState.CANCELLED, OrderState.FAILED, OrderState.REJECTED)
        for order in orders['results']:
            if OrderState(order['state']) not in stoppedOrderStates:
                r = self.cancel_order(oid=order['id'])
                if r.status_code == 200:
                    res['cancelled'].append(order['id'])
                else:
                    res['error'].append(order['id'])
        return(res)
