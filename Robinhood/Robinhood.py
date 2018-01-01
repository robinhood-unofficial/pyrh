"""Robinhood.py: a collection of utilities for working with Robinhood's Private API """

import logging
import warnings

from six.moves.urllib.parse import unquote
from six.moves.urllib.request import getproxies
from six.moves import input

from enum import Enum

import getpass
import requests
import six

from . import exceptions as RH_exception

class Robinhood:
    """Wrapper class for fetching/parsing Robinhood endpoints """

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

        def stopped(self):
            return self.name in ('FILLED', 'CANCELLED', 'REJECTED', 'FAILED')
        def active(self):
            return self.name in ('QUEUED', 'CONFIRMED', 'PARTIALLY_FILLED')
        def other(self):
            return self.name in ('UNCONFIRMED')

    ###########################################################################
    #                       Logging in and initializing
    ###########################################################################

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
        """Prompts user for username and password and calls login() """

        username = input("Username: ")
        password = getpass.getpass()

        return self.login(username=username, password=password)


    def login(self,
              username,
              password,
              mfa_code=None):
        """Save and test login info for Robinhood accounts

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
            res = self.session.post(self.endpoints['login'], data=payload)
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
        """Logout from Robinhood

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


    ###########################################################################
    #                               GET DATA
    ###########################################################################

    def investment_profile(self):
        """Fetch investment_profile """

        res = self.session.get(self.endpoints['investment_profile'])
        res.raise_for_status()  #will throw without auth
        data = res.json()

        return data

    def instruments(self, query=None, symbol=None, instrument=None):
        """fetch instruments endpoint

        Args:
            query (str): search for ticker, e.g. by company name
            symbol (str): find instrument by it's symbol
            instrument (dict|str): valid instrument representation

        Returns:
            (:obj:`dict`): JSON contents from `instruments` endpoint

            Returns:
                (:obj:`dict`): JSON contents from `instruments` endpoint
        """
        res = None
        if instrument:
            res = self.session.get(
                self.instrument_url(instrument)
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
        if 'results' not in res:
            return res
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
        raise ValueError("Invalid instrumentid passed")

    def quote_data(self, stock):
        """fetch single stock quote

        Args:
            stock (str): stock ticker, prompt if blank

            Args:
                id (str): instrument id

            Returns:
                (:obj:`dict`): JSON dict of instrument
        """
        url = str(self.endpoints['quotes']) + str(stock) + "/"

        # Check for validity of symbol
        try:
            res = requests.get(url)
            res.raise_for_status()
        except requests.exceptions.HTTPError:
            raise RH_exception.InvalidTickerSymbol()


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
        if isinstance(stocks,str):
            stocks = [stocks]

        url = str(self.endpoints['quotes']) + "?symbols=" + ",".join(stocks)

        try:
            res = requests.get(url)
            res.raise_for_status()
        except requests.exceptions.HTTPError:
            raise RH_exception.InvalidTickerSymbol()


        return res.json()["results"]


    def get_quote_list(self,
                       stock='',
                       key=''):
        """Returns multiple stock info and keys from quote_data (prompt if blank)

            Args:
                stock (str): stock ticker (or tickers separated by a comma)
                , prompt if blank
                key (str): key attributes that the function should return

        Returns:
            (:obj:`list`): Returns values from each stock or empty list
                           if none of the stocks were valid
                           requested fields are returned in an array

        """

        if isinstance(key,str):
            keys = key.split(',')
        else:
            keys = [key]

        #Creates a tuple containing the information we want to retrieve
        def append_stock(stock):
            res = []
            for item in keys:
                res.append(stock[item])
            return res

        #Prompt for stock if not entered
        if not stock:   #pragma: no cover
            stock = input("Symbol: ")
        data = self.quotes_data(stock)

        res = []

        # Handles the case of multple tickers
        if isinstance(data, list):
            for stock in data:
                if stock == None:
                    continue
                res.append(append_stock(stock))

        else:
            res.append(append_stock(data))

        return res


    def get_quote(self, stock=''):
        """Wrapper for quote_data """

        data = self.quote_data(stock)
        return data

    def get_quotes_fields(self, stocks=None, fields=''):
        """Returns multiple stock info and fields from quote_data

        Args:
            stock (str|list): stock ticker(s) can be one or a list
            fields (str|list): fields of the quote data that should return

        Returns:
            (:obj:`dict`): Dict with dict of the requested field values for stock
        """
        data = self.quotes_data(stocks)

        # XXX Arguably fields should also be a list of Enum to catch typos
        if isinstance(fields,str):
            fields = [fields]

        res = {}
        for quote in data:
            if not isinstance(quote,dict):
                raise Warning("Returned quote was not a dict")

            # XXX what if symbol is non-unique should we use instrument as key here?
            symbol = quote['symbol']
            if len(fields):
                res[symbol] = {key: value for (key, value) in quote.items() if key in fields}
            else:
                res[symbol] = quote

        return res

    def get_historical_quotes(
            self,
            stock,
            interval,
            span,
            bounds='regular'
        ):
        """fetch historical data for stock

        Note: valid interval/span configs
            interval = 5minute | 10minute + span = day, week
            interval = day + span = year
            interval = week
            TODO: NEEDS TESTS

        Args:
            stock (list|str): stock ticker(s)
            interval (str): resolution of data
            span (str): length of data
            bounds (:enum:`Bounds`, optional): 'extended' or 'regular' trading hours

            Args:
                stock (str): stock ticker
                interval (str): resolution of data
                span (str): length of data
                bounds (:enum:`Bounds`, optional): 'extended' or 'regular' trading hours

            Returns:
                (:obj:`dict`) values returned from `historicals` endpoint
        """
        # recast to Enum
        bounds = self.Bounds(bounds)

        if isinstance(stock,str):
            stock = [stock]

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
        """Fetch news endpoint
            Args:
                stock (str): stock ticker

            Returns:
                (:obj:`dict`) values returned from `news` endpoint
        """
        res = self.session.get(self.endpoints['news']+stock.upper()+"/")
        res.raise_for_status()
        return res.json()

    def print_quote(self, stock=''):    #pragma: no cover
        """Print quote information
            Args:
                stock (str): ticker to fetch

            Returns:
                None
        """
        quotes = self.get_quotes_fields(stocks=stock,fields=('last_trade_price'))
        for stock, quote in quotes.items()  :
            quote_str = stock + ": $" + quote['last_trade_price']
            print(quote_str)
            self.logger.info(quote_str)


    def print_quotes(self, stocks): #pragma: no cover
        """Print a collection of stocks

            Args:
                stocks (:obj:`list`): list of stocks to pirnt

            Returns:
                None
        """

        if stocks is None:
            return

        for stock in stocks:
            self.print_quote(stock)


    def ask_price(self, stock=''):
        """Get asking price for a stock

            Note:
                queries `quote` endpoint, dict wrapper

            Args:
                stock (str): stock ticker

            Returns:
                (float): ask price
        """

        return self.get_quote_list(stock,'ask_price')


    def ask_size(self, stock=''):
        """Get ask size for a stock

            Note:
                queries `quote` endpoint, dict wrapper

            Args:
                stock (str): stock ticker

            Returns:
                (int): ask size
        """

        return self.get_quote_list(stock,'ask_size')


    def bid_price(self, stock=''):
        """Get bid price for a stock

            Note:
                queries `quote` endpoint, dict wrapper

            Args:
                stock (str): stock ticker

            Returns:
                (float): bid price
        """

        return self.get_quote_list(stock,'bid_price')


    def bid_size(self, stock=''):
        """Get bid size for a stock

            Note:
                queries `quote` endpoint, dict wrapper

            Args:
                stock (str): stock ticker

            Returns:
                (int): bid size
        """

        return self.get_quote_list(stock,'bid_size')


    def last_trade_price(self, stock=''):
        """Get last trade price for a stock

            Note:
                queries `quote` endpoint, dict wrapper

            Args:
                stock (str): stock ticker

            Returns:
                (float): last trade price
        """

        return self.get_quote_list(stock,'last_trade_price')


    def previous_close(self, stock=''):
        """Get previous closing price for a stock

            Note:
                queries `quote` endpoint, dict wrapper

            Args:
                stock (str): stock ticker

            Returns:
                (float): previous closing price
        """

        return self.get_quote_list(stock,'previous_close')


    def previous_close_date(self, stock=''):
        """Get previous closing date for a stock

            Note:
                queries `quote` endpoint, dict wrapper

            Args:
                stock (str): stock ticker

            Returns:
                (str): previous close date
        """

        return self.get_quote_list(stock,'previous_close_date')


    def adjusted_previous_close(self, stock=''):
        """Get adjusted previous closing price for a stock

            Note:
                queries `quote` endpoint, dict wrapper

            Args:
                stock (str): stock ticker

            Returns:
                (float): adjusted previous closing price
        """

        return self.get_quote_list(stock,'adjusted_previous_close')


    def symbol(self, stock=''):
        """Get symbol for a stock

            Note:
                queries `quote` endpoint, dict wrapper

            Args:
                stock (str): stock ticker

            Returns:
                (str): stock symbol
        """

        return self.get_quote_list(stock,'symbol')


    def last_updated_at(self, stock=''):
        """Get last update datetime

            Note:
                queries `quote` endpoint, dict wrapper

            Args:
                stock (str): stock ticker

            Returns:
                (str): last update datetime
        """

        return self.get_quote_list(stock, 'last_updated_at')


    def last_updated_at_datetime(self, stock=''):
        """Get last updated datetime

            Note:
                queries `quote` endpoint, dict wrapper
                `self.last_updated_at` returns time as `str` in format: 'YYYY-MM-ddTHH:mm:ss:000Z'

            Args:
                stock (str): stock ticker

            Returns:
                (datetime): last update datetime

        """

        #Will be in format: 'YYYY-MM-ddTHH:mm:ss:000Z'
        datetime_string = self.last_updated_at(stock)
        result = dateutil.parser.parse(datetime_string)

        return result


    def get_account(self):
        """Fetch account information

            Returns:
                (:obj:`dict`): `accounts` endpoint payload
        """

        res = self.session.get(self.endpoints['accounts'])
        res.raise_for_status()  #auth required
        res = res.json()

        return res['results'][0]


    def get_url(self, url):
        """
            Flat wrapper for fetching URL directly
        """

        return self.session.get(url).json()


    ###########################################################################
    #                           GET FUNDAMENTALS
    ###########################################################################

    def get_fundamentals(self, stock=''):
        """Find stock fundamentals data

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
            raise RH_exception.InvalidTickerSymbol()


        return res.json()

    def fundamentals(self, stock=''):
        """Wrapper for get_fundamentlals function """

        return self.get_fundamentals(stock)


    ###########################################################################
    #                           PORTFOLIOS DATA
    ###########################################################################

    def portfolios(self):
        """Returns the user's portfolio data """

        req = self.session.get(self.endpoints['portfolios'])
        req.raise_for_status()

        return req.json()['results'][0]


    def adjusted_equity_previous_close(self):
        """Wrapper for portfolios

            Returns:
                (float): `adjusted_equity_previous_close` value

        """

        return float(self.portfolios()['adjusted_equity_previous_close'])


    def equity(self):
        """Wrapper for portfolios

            Returns:
                (float): `equity` value
        """

        return float(self.portfolios()['equity'])


    def equity_previous_close(self):
        """Wrapper for portfolios

            Returns:
                (float): `equity_previous_close` value
        """

        return float(self.portfolios()['equity_previous_close'])


    def excess_margin(self):
        """Wrapper for portfolios

            Returns:
                (float): `excess_margin` value
        """

        return float(self.portfolios()['excess_margin'])


    def extended_hours_equity(self):
        """Wrapper for portfolios

            Returns:
                (float): `extended_hours_equity` value
        """

        try:
            return float(self.portfolios()['extended_hours_equity'])
        except TypeError:
            return None


    def extended_hours_market_value(self):
        """Wrapper for portfolios

            Returns:
                (float): `extended_hours_market_value` value
        """

        try:
            return float(self.portfolios()['extended_hours_market_value'])
        except TypeError:
            return None


    def last_core_equity(self):
        """Wrapper for portfolios

            Returns:
                (float): `last_core_equity` value
        """

        return float(self.portfolios()['last_core_equity'])


    def last_core_market_value(self):
        """Wrapper for portfolios

            Returns:
                (float): `last_core_market_value` value
        """

        return float(self.portfolios()['last_core_market_value'])


    def market_value(self):
        """Wrapper for portfolios

            Returns:
                (float): `market_value` value
        """

        return float(self.portfolios()['market_value'])

    def instrument_url(self,instrument=None):
        """

        return the canonical instrument URL given either an instrument dict object or string
        that represents and instrument

        Args:
            instrument (string): RH instrument URL, instrumentid or instrument object
        """
        url = None
        if isinstance(instrument, dict) and 'url' in instrument:
            url = instrument['url']
        elif isinstance(instrument, str) and instrument is not None:
            if instrument.startswith( self.endpoints['instruments'] ):
                url = instrument
            if len(instrument) >= 36 and not "/" in instrument:
                url = self.endpoints['instrumentid'].format(instrumentid=instrument)

        if not url:
            raise ValueError("Invalid instrument reference passed: %s %s " % (type(instrument), instrument))

        return url

    def order_history(self,instrument=None):
        """Wrapper for portfolios

        Args:
            instrument (dict|str): valid instrument representation
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
            data['instrument'] = self.instrument_url(instrument)
        res = self.session.get(self.endpoints['orders'], params=data)
        res.raise_for_status()
        return res.json()


    def dividends(self):
        """Wrapper for portfolios

            Returns:
                (:obj: `dict`): JSON dict from getting dividends
        """

        return self.session.get(self.endpoints['dividends']).json()


    ###########################################################################
    #                           POSITIONS DATA
    ###########################################################################

    def positions(self):
        """Returns the user's positions data

            Returns:
                (:object: `dict`): JSON dict from getting positions
        """

        return self.session.get(self.endpoints['positions']).json()

    def securities_owned(self):
        """Returns list of securities' symbols that the user has shares in

            Returns:
                (:object: `dict`): Non-zero positions
        """

        return self.session.get(self.endpoints['positions']+'?nonzero=true').json()

    ###########################################################################
    #                               PLACE ORDER
    ###########################################################################

    def place_order(self,
            instrument,
            quantity,
            transaction,
            bid_price=None,
            stop_price=None,
            trigger='immediate',
            order='market',
            time_in_force = 'gfd'
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
                transaction (:enum:`Transaction`): BUY or SELL
                trigger (:enum:`Trigger`): IMMEDIATE or STOP
                order (:enum:`Order`): MARKET or LIMIT
                time_in_force (:enum:`TimeForce`): GFD or GTC (day or until cancelled)

            Returns:
                (:obj:`requests.request`): result from `orders` put command
        """
        # Insure the order instructions are valid
        transaction = self.Transaction(transaction)
        trigger = self.Trigger(trigger)
        order = self.Order(order)
        time_in_force = self.TimeForce(time_in_force)

        if order == self.Order.LIMIT and bid_price is None:
            raise ValueError("Order.LIMIT without bid_price")

        if bid_price is not None and not order == self.Order.LIMIT:
            raise ValueError("bid_price without Order.LIMIT")

        # If Order.MARKET then we still need to pass RH a price, RH places market orders
        # automatically as limit orders with a 5% buffer
        if not bid_price and order == self.Order.MARKET:
            bid_price = bid_price(instrument['symbol'])

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

        if trigger == self.Trigger.STOP:
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
            bid_price
    ):
        """Wrapper for placing buy orders

            Args:
                instrument (dict): the RH URL and symbol in dict for the instrument to be traded
                quantity (int): quantity of stocks in order
                bid_price (float): price for order

            Returns:
                (:obj:`requests.request`): result from `orders` put command

        """
        transaction = self.Transaction.BUY
        return self.place_order(instrument, quantity, bid_price, transaction)

    def place_sell_order(self,
                         instrument,
                         quantity,
                         bid_price):
        """Wrapper for placing sell orders

            Args:
                instrument (dict): the RH URL and symbol in dict for the instrument to be traded
                quantity (int): quantity of stocks in order
                bid_price (float): price for order

            Returns:
                (:obj:`requests.request`): result from `orders` put command
        """
        transaction = self.Transaction.SELL
        return self.place_order(instrument, quantity, bid_price, transaction)

    # Methods below here are a complete rewrite for buying and selling
    # These are new. Use at your own risk!

    def place_market_buy_order(self,
                               instrument_URL = None,
                               symbol = None,
                               time_in_force = None,
                               quantity = None):
        """Wrapper for placing market buy orders

            Notes:
                If only one of the instrument_URL or symbol are passed as
                arguments the other will be looked up automatically.

            Args:
                instrument_URL (str): The RH URL of the instrument
                symbol (str): The ticker symbol of the instrument
                time_in_force (str): 'GFD' or 'GTC' (day or until cancelled)
                quantity (int): Number of shares to buy

            Returns:
                (:obj:`requests.request`): result from `orders` put command
        """
        return(self.submit_order(order_type = 'market',
                                 trigger = 'immediate',
                                 side = 'buy',
                                 instrument_URL = instrument_URL,
                                 symbol = symbol,
                                 time_in_force = time_in_force,
                                 quantity = quantity))

    def place_limit_buy_order(self,
                              instrument_URL = None,
                              symbol = None,
                              time_in_force = None,
                              price = None,
                              quantity = None):
        """Wrapper for placing limit buy orders

            Notes:
                If only one of the instrument_URL or symbol are passed as
                arguments the other will be looked up automatically.

            Args:
                instrument_URL (str): The RH URL of the instrument
                symbol (str): The ticker symbol of the instrument
                time_in_force (str): 'GFD' or 'GTC' (day or until cancelled)
                price (float): The max price you're willing to pay per share
                quantity (int): Number of shares to buy

            Returns:
                (:obj:`requests.request`): result from `orders` put command
        """
        return(self.submit_order(order_type = 'limit',
                                 trigger = 'immediate',
                                 side = 'buy',
                                 instrument_URL = instrument_URL,
                                 symbol = symbol,
                                 time_in_force = time_in_force,
                                 price = price,
                                 quantity = quantity))

    def place_stop_loss_buy_order(self,
                                  instrument_URL = None,
                                  symbol = None,
                                  time_in_force = None,
                                  stop_price = None,
                                  quantity = None):
        """Wrapper for placing stop loss buy orders

            Notes:
                If only one of the instrument_URL or symbol are passed as
                arguments the other will be looked up automatically.

            Args:
                instrument_URL (str): The RH URL of the instrument
                symbol (str): The ticker symbol of the instrument
                time_in_force (str): 'GFD' or 'GTC' (day or until cancelled)
                stop_price (float): The price at which this becomes a market order
                quantity (int): Number of shares to buy

            Returns:
                (:obj:`requests.request`): result from `orders` put command
        """
        return(self.submit_order(order_type = 'market',
                                 trigger = 'stop',
                                 side = 'buy',
                                 instrument_URL = instrument_URL,
                                 symbol = symbol,
                                 time_in_force = time_in_force,
                                 stop_price = stop_price,
                                 quantity = quantity))

    def place_stop_limit_buy_order(self,
                                   instrument_URL = None,
                                   symbol = None,
                                   time_in_force = None,
                                   stop_price = None,
                                   price = None,
                                   quantity = None):
        """Wrapper for placing stop limit buy orders

            Notes:
                If only one of the instrument_URL or symbol are passed as
                arguments the other will be looked up automatically.

            Args:
                instrument_URL (str): The RH URL of the instrument
                symbol (str): The ticker symbol of the instrument
                time_in_force (str): 'GFD' or 'GTC' (day or until cancelled)
                stop_price (float): The price at which this becomes a limit order
                price (float): The max price you're willing to pay per share
                quantity (int): Number of shares to buy

            Returns:
                (:obj:`requests.request`): result from `orders` put command
        """
        return(self.submit_order(order_type = 'limit',
                                 trigger = 'stop',
                                 side = 'buy',
                                 instrument_URL = instrument_URL,
                                 symbol = symbol,
                                 time_in_force = time_in_force,
                                 stop_price = stop_price,
                                 price = price,
                                 quantity = quantity))

    def place_market_sell_order(self,
                                instrument_URL = None,
                                symbol = None,
                                time_in_force = None,
                                quantity = None):
        """Wrapper for placing market sell orders

            Notes:
                If only one of the instrument_URL or symbol are passed as
                arguments the other will be looked up automatically.

            Args:
                instrument_URL (str): The RH URL of the instrument
                symbol (str): The ticker symbol of the instrument
                time_in_force (str): 'GFD' or 'GTC' (day or until cancelled)
                quantity (int): Number of shares to sell

            Returns:
                (:obj:`requests.request`): result from `orders` put command
        """
        return(self.submit_order(order_type = 'market',
                                 trigger = 'immediate',
                                 side = 'sell',
                                 instrument_URL = instrument_URL,
                                 symbol = symbol,
                                 time_in_force = time_in_force,
                                 quantity= quantity))

    def place_limit_sell_order(self,
                               instrument_URL = None,
                               symbol = None,
                               time_in_force = None,
                               price = None,
                               quantity = None):
        """Wrapper for placing limit sell orders

            Notes:
                If only one of the instrument_URL or symbol are passed as
                arguments the other will be looked up automatically.

            Args:
                instrument_URL (str): The RH URL of the instrument
                symbol (str): The ticker symbol of the instrument
                time_in_force (str): 'GFD' or 'GTC' (day or until cancelled)
                price (float): The minimum price you're willing to get per share
                quantity (int): Number of shares to sell

            Returns:
                (:obj:`requests.request`): result from `orders` put command
        """
        return(self.submit_order(order_type = 'limit',
                                 trigger = 'immediate',
                                 side = 'sell',
                                 instrument_URL = instrument_URL,
                                 symbol = symbol,
                                 time_in_force = time_in_force,
                                 price = price,
                                 quantity = quantity))

    def place_stop_loss_sell_order(self,
                                   instrument_URL = None,
                                   symbol = None,
                                   time_in_force = None,
                                   stop_price = None,
                                   quantity = None):
        """Wrapper for placing stop loss sell orders

            Notes:
                If only one of the instrument_URL or symbol are passed as
                arguments the other will be looked up automatically.

            Args:
                instrument_URL (str): The RH URL of the instrument
                symbol (str): The ticker symbol of the instrument
                time_in_force (str): 'GFD' or 'GTC' (day or until cancelled)
                stop_price (float): The price at which this becomes a market order
                quantity (int): Number of shares to sell

            Returns:
                (:obj:`requests.request`): result from `orders` put command
        """
        return(self.submit_order(order_type = 'market',
                                 trigger = 'stop',
                                 side = 'sell',
                                 instrument_URL = instrument_URL,
                                 symbol = symbol,
                                 time_in_force = time_in_force,
                                 stop_price = stop_price,
                                 quantity = quantity))

    def place_stop_limit_sell_order(self,
                                    instrument_URL = None,
                                    symbol = None,
                                    time_in_force = None,
                                    price = None,
                                    stop_price = None,
                                    quantity = None):
        """Wrapper for placing stop limit sell orders

            Notes:
                If only one of the instrument_URL or symbol are passed as
                arguments the other will be looked up automatically.

            Args:
                instrument_URL (str): The RH URL of the instrument
                symbol (str): The ticker symbol of the instrument
                time_in_force (str): 'GFD' or 'GTC' (day or until cancelled)
                stop_price (float): The price at which this becomes a limit order
                price (float): The max price you're willing to get per share
                quantity (int): Number of shares to sell

            Returns:
                (:obj:`requests.request`): result from `orders` put command
        """
        return(self.submit_order(order_type = 'limit',
                                 trigger = 'stop',
                                 side = 'sell',
                                 instrument_URL = instrument_URL,
                                 symbol = symbol,
                                 time_in_force = time_in_force,
                                 stop_price = stop_price,
                                 price = price,
                                 quantity = quantity))

    def submit_order(self,
                     instrument_URL = None,
                     symbol = None,
                     order_type = None,
                     time_in_force = None,
                     trigger = None,
                     price = None,
                     stop_price = None,
                     quantity = None,
                     side = None):
        """Submits order to Robinhood

            Notes:
                This is normally not called directly.  Most programs should use
                one of the following instead:

                    place_market_buy_order()
                    place_limit_buy_order()
                    place_stop_loss_buy_order()
                    place_stop_limit_buy_order()
                    place_market_sell_order()
                    place_limit_sell_order()
                    place_stop_loss_sell_order()
                    place_stop_limit_sell_order()

            Args:
                instrument_URL (str): the RH URL for the instrument
                symbol (str): the ticker symbol for the instrument
                order_type (str): 'MARKET' or 'LIMIT'
                time_in_force (:enum:`TIME_IN_FORCE`): GFD or GTC (day or
                                                       until cancelled)
                trigger (str): IMMEDIATE or STOP enum
                price (float): The share price you'll accept
                stop_price (float): The price at which the order becomes a
                                    market or limit order
                quantity (int): The number of shares to buy/sell
                side (str): BUY or sell

            Returns:
                (:obj:`requests.request`): result from `orders` put command
        """

        # Start with some parameter checks. I'm paranoid about $.
        if(instrument_URL is None):
            if(symbol is None):
                raise(valueError('Neither instrument_URL nor symbol were passed to submit_order'))
            instrument_URL = self.instruments(symbol)[0]['url']

        if(symbol is None):
            symbol = self.session.get(instrument_URL).json()['symbol']

        if(side is None):
            raise(valueError('Order is neither buy nor sell in call to submit_order'))

        if(order_type == None):
            if(price == None):
                if(stop_price == None):
                    order_type = 'market'
                else:
                    order_type = 'limit'

        symbol = str(symbol).upper()
        order_type = str(order_type).lower()
        time_in_force = str(time_in_force).lower()
        trigger = str(trigger).lower()
        side = str(side).lower()

        if(order_type != 'market') and (order_type != 'limit'):
            raise(valueError('Invalid order_type in call to submit_order'))

        if(order_type == 'limit'):
            if(price is None):
                raise(valueError('Limit order has no price in call to submit_order'))
            if(price <= 0):
                raise(valueError('Price must be positive number in call to submit_order'))

        if(trigger == 'stop'):
            if(stop_price is None):
                raise(valueError('Stop order has no stop_price in call to submit_order'))
            if(price <= 0):
                raise(valueError('Stop_price must be positive number in call to submit_order'))

        if(stop_price is not None):
            if(trigger != 'stop'):
                raise(valueError('Stop price set for non-stop order in call to submit_order'))

        if(price is None):
            if(order_type == 'limit'):
                raise(valueError('Limit order has no price in call to submit_order'))

        if(price is not None):
            if(order_type.lower() == 'market'):
                raise(valueError('Market order has price limit in call to submit_order'))

        price = float(price)

        if(quantity is None):
            raise(valueError('No quantity specified in call to submit_order'))

        quantity = int(quantity)

        if(quantity <= 0):
            raise(valueError('Quantity must be positive number in call to submit_order'))

        payload = {}

        for field,value in [('account',self.get_account()['url']),
                            ('instrument',instrument_URL),
                            ('symbol',symbol),
                            ('type',order_type),
                            ('time_in_force', time_in_force),
                            ('trigger',trigger),
                            ('price',price),
                            ('stop_price',stop_price),
                            ('quantity',quantity),
                            ('side',side)]:
            if(value is not None):
                payload[field] = value

        res = self.session.post(self.endpoints['orders'], data=payload)
        res.raise_for_status()

        return res

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
            instrument (dict|str): valid instrument representation

        Returns:
            (:obj:`dict`): containing keys 'cancelled' or 'error' with the list of order ids
        """
        orders = self.order_history(instrument=self.instrument_url(instrument))
        res = {'cancelled':[], 'error':[]}

        for order in orders['results']:
            if not self.OrderState(order['state']).stopped():
                r = self.cancel_order(oid=order['id'])
                if r.status_code == 200:
                    res['cancelled'].append(order['id'])
                else:
                    res['error'].append(order['id'])
        return(res)
