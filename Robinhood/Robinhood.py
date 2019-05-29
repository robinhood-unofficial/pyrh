"""Robinhood.py: a collection of utilities for working with Robinhood's Private API """

#Standard libraries
import logging
import warnings

from enum import Enum

#External dependencies
from six.moves.urllib.parse import unquote  # pylint: disable=E0401
from six.moves.urllib.request import getproxies  # pylint: disable=E0401
from six.moves import input

import getpass
import requests
import six
import dateutil
import time
import random
import hmac, base64, struct, hashlib

#Application-specific imports
from . import exceptions as RH_exception
from . import endpoints

class Bounds(Enum):
    """Enum for bounds in `historicals` endpoint """

    REGULAR = 'regular'
    EXTENDED = 'extended'


class Transaction(Enum):
    """Enum for buy/sell orders """

    BUY = 'buy'
    SELL = 'sell'


class Robinhood:
    """Wrapper class for fetching/parsing Robinhood endpoints """

    session = None
    username = None
    password = None
    headers = None
    auth_token = None
    refresh_token = None

    logger = logging.getLogger('Robinhood')
    logger.addHandler(logging.NullHandler())

    client_id = "c82SH0WZOsabOXGP2sxqcj34FxkvfnWRZBKlBjFS"


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
        self.device_token = ""
        self.challenge_id = ""

    def login_required(function):  # pylint: disable=E0213
        """ Decorator function that prompts user for login if they are not logged in already. Can be applied to any function using the @ notation. """
        def wrapper(self, *args, **kwargs):
            if 'Authorization' not in self.headers:
                self.auth_method()
            return function(self, *args, **kwargs)  # pylint: disable=E1102
        return wrapper
        
    def GenerateDeviceToken(self):
        rands = []
        for i in range(0,16):
            r = random.random()
            rand = 4294967296.0 * r
            rands.append((int(rand) >> ((3 & i) << 3)) & 255)

        hexa = []
        for i in range(0,256):
            hexa.append(str(hex(i+256)).lstrip("0x").rstrip("L")[1:])

        id = ""
        for i in range(0,16):
            id += hexa[rands[i]]

            if (i == 3) or (i == 5) or (i == 7) or (i == 9):
                id += "-"

        self.device_token = id

    def get_mfa_token(self, secret):
        intervals_no = int(time.time())//30
        key = base64.b32decode(secret, True)
        msg = struct.pack(">Q", intervals_no)
        h = hmac.new(key, msg, hashlib.sha1).digest()
        o = h[19] & 15
        h = '{0:06d}'.format((struct.unpack(">I", h[o:o+4])[0] & 0x7fffffff) % 1000000)
        return h

    def login(self,
              username,
              password,
              qr_code=None):
        """Save and test login info for Robinhood accounts
        Args:
            username (str): username
            password (str): password
            qr_code (str): QR code that will be used to generate mfa_code (optional but recommended)
            To get QR code, set up 2FA in Security, get Authentication App, and click "Can't Scan It?"
        Returns:
            (bool): received valid auth token
        """
        self.username = username
        self.password = password
        
        if self.device_token == "":
                self.GenerateDeviceToken()
        
        if qr_code:
            self.qr_code = qr_code
            payload = {
                'password': self.password,
                'username': self.username,
                'grant_type': 'password',
                'client_id': "c82SH0WZOsabOXGP2sxqcj34FxkvfnWRZBKlBjFS",
                'scope': 'internal',
                'device_token': self.device_token,
                'mfa_code': self.get_mfa_token(self.qr_code)
            }
            
            try:
                res = self.session.post(endpoints.login(), data=payload, timeout=15)
                data = res.json()
                
                if 'access_token' in data.keys() and 'refresh_token' in data.keys():
                    self.auth_token = data['access_token']
                    self.refresh_token = data['refresh_token']
                    self.headers['Authorization'] = 'Bearer ' + self.auth_token
                    return True
                
            except requests.exceptions.HTTPError:
                raise RH_exception.LoginFailed()

        else:
            payload = {
                'password': self.password,
                'username': self.username,
                'grant_type': 'password',
                'client_id': "c82SH0WZOsabOXGP2sxqcj34FxkvfnWRZBKlBjFS",
                'expires_in': '86400',
                'scope': 'internal',
                'device_token': self.device_token,
                'challenge_type': 'sms'
            }

            try:
                res = self.session.post(endpoints.login(), data=payload, timeout=15)
                response_data = res.json()
                if self.challenge_id == "" and "challenge" in response_data.keys():
                    self.challenge_id = response_data["challenge"]["id"]
                self.headers["X-ROBINHOOD-CHALLENGE-RESPONSE-ID"] = self.challenge_id #has to add this to stay logged in
                sms_challenge_endpoint = "https://api.robinhood.com/challenge/{}/respond/".format(self.challenge_id)
                print("No 2FA Given")
                print("SMS Code:")
                self.sms_code = input()
                challenge_res = {"response":self.sms_code}
                res2 = self.session.post(sms_challenge_endpoint, data=challenge_res, timeout=15)
                res2.raise_for_status()
                #gets access token for final response to stay logged in
                res3 = self.session.post(endpoints.login(), data=payload, timeout=15)
                res3.raise_for_status()
                data = res3.json()

                if 'access_token' in data.keys() and 'refresh_token' in data.keys():
                    self.auth_token = data['access_token']
                    self.refresh_token = data['refresh_token']
                    self.headers['Authorization'] = 'Bearer ' + self.auth_token
                    return True

            except requests.exceptions.HTTPError:
                raise RH_exception.LoginFailed()

        return False
    
    def auth_method(self):
        
        if self.qr_code:
            payload = {
                'password': self.password,
                'username': self.username,
                'grant_type': 'password',
                'client_id': "c82SH0WZOsabOXGP2sxqcj34FxkvfnWRZBKlBjFS",
                'scope': 'internal',
                'device_token': self.device_token,
                'mfa_code': self.get_mfa_token(self.qr_code)
            }
            
            try:
                res = self.session.post(endpoints.login(), data=payload, timeout=15)
                data = res.json()
                
                if 'access_token' in data.keys() and 'refresh_token' in data.keys():
                    self.auth_token = data['access_token']
                    self.refresh_token = data['refresh_token']
                    self.headers['Authorization'] = 'Bearer ' + self.auth_token
                    return True
                
            except requests.exceptions.HTTPError:
                raise RH_exception.LoginFailed()

        else:        
            payload = {
                'password': self.password,
                'username': self.username,
                'grant_type': 'password',
                'client_id': "c82SH0WZOsabOXGP2sxqcj34FxkvfnWRZBKlBjFS",
                'expires_in': '86400',
                'scope': 'internal',
                'device_token': self.device_token,
            }

            try:
                res = self.session.post(endpoints.login(), data=payload, timeout=15)
                res.raise_for_status()
                data = res.json()

                if 'access_token' in data.keys() and 'refresh_token' in data.keys():
                    self.auth_token = data['access_token']
                    self.refresh_token = data['refresh_token']
                    self.headers['Authorization'] = 'Bearer ' + self.auth_token
                    return True

            except requests.exceptions.HTTPError:
                raise RH_exception.LoginFailed()
    
        return False
    
    def logout(self):
        """Logout from Robinhood

        Returns:
            (:obj:`requests.request`) result from logout endpoint

        """

        try:
            payload = {
                'client_id': self.client_id,
                'token': self.refresh_token
            }
            req = self.session.post(endpoints.logout(), data=payload, timeout=15)
            req.raise_for_status()
        except requests.exceptions.HTTPError as err_msg:
            warnings.warn('Failed to log out ' + repr(err_msg))

        self.headers['Authorization'] = None
        self.auth_token = None

        return req


    ###########################################################################
    #                               GET DATA
    ###########################################################################

    def investment_profile(self):
        """Fetch investment_profile """

        res = self.session.get(endpoints.investment_profile(), timeout=15)
        res.raise_for_status()  # will throw without auth
        data = res.json()

        return data


    def instruments(self, stock):
        """Fetch instruments endpoint

            Args:
                stock (str): stock ticker

            Returns:
                (:obj:`dict`): JSON contents from `instruments` endpoint
        """

        res = self.session.get(endpoints.instruments(), params={'query': stock.upper()}, timeout=15)
        res.raise_for_status()
        res = res.json()

        # if requesting all, return entire object so may paginate with ['next']
        if (stock == ""):
            return res

        return res['results']


    def instrument(self, id):
        """Fetch instrument info

            Args:
                id (str): instrument id

            Returns:
                (:obj:`dict`): JSON dict of instrument
        """
        url = str(endpoints.instruments()) + "?symbol=" + str(id)

        try:
            req = requests.get(url, timeout=15)
            req.raise_for_status()
            data = req.json()
        except requests.exceptions.HTTPError:
            raise RH_exception.InvalidInstrumentId()

        return data['results'][0]


    def quote_data(self, stock=''):
        """Fetch stock quote

            Args:
                stock (str or dict): stock ticker symbol or stock instrument

            Returns:
                (:obj:`dict`): JSON contents from `quotes` endpoint
        """

        if isinstance(stock, dict):
            if "symbol" in stock.keys():
                url = str(endpoints.quotes()) + stock["symbol"] + "/"
        elif isinstance(stock, str):
            url = str(endpoints.quotes()) + stock + "/"
        elif isinstance(stock, unicode):
            url = str(endpoints.quotes()) + str(stock) + "/"
        else:
            raise RH_exception.InvalidTickerSymbol()

        #Check for validity of symbol
        try:
            req = self.session.get(url, headers=self.headers, timeout=15)
            req.raise_for_status()
            data = req.json()
        except requests.exceptions.HTTPError:
            raise RH_exception.InvalidTickerSymbol()


        return data


    # We will keep for compatibility until next major release
    def quotes_data(self, stocks):
        """Fetch quote for multiple stocks, in one single Robinhood API call

            Args:
                stocks (list<str>): stock tickers

            Returns:
                (:obj:`list` of :obj:`dict`): List of JSON contents from `quotes` endpoint, in the
                    same order of input args. If any ticker is invalid, a None will occur at that position.
        """

        url = str(endpoints.quotes()) + "?symbols=" + ",".join(stocks)

        try:
            req = self.session.get(url, timeout=15)
            req.raise_for_status()
            data = req.json()
        except requests.exceptions.HTTPError:
            raise RH_exception.InvalidTickerSymbol()


        return data["results"]


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

        """

        #Creates a tuple containing the information we want to retrieve
        def append_stock(stock):
            keys = key.split(',')
            myStr = ''
            for item in keys:
                myStr += stock[item] + ","

            return (myStr.split(','))


        #Prompt for stock if not entered
        if not stock:   # pragma: no cover
            stock = input("Symbol: ")

        data = self.quote_data(stock)
        res = []

        # Handles the case of multple tickers
        if stock.find(',') != -1:
            for stock in data['results']:
                if stock is None:
                    continue
                res.append(append_stock(stock))

        else:
            res.append(append_stock(data))

        return res


    def get_quote(self, stock=''):
        """Wrapper for quote_data """

        data = self.quote_data(stock)
        return data

    def get_historical_quotes(self, stock, interval, span, bounds=Bounds.REGULAR):
        """Fetch historical data for stock

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
        if type(stock) is str:
            stock = [stock]

        if isinstance(bounds, str):  # recast to Enum
            bounds = Bounds(bounds)

        historicals = endpoints.historicals() + "/?symbols=" + ','.join(stock).upper() + "&interval=" + interval + "&span=" + span + "&bounds=" + bounds.name.lower()

        res = self.session.get(historicals, timeout=15)
        return res.json()


    def get_news(self, stock):
        """Fetch news endpoint
            Args:
                stock (str): stock ticker

            Returns:
                (:obj:`dict`) values returned from `news` endpoint
        """

        return self.session.get(endpoints.news(stock.upper()), timeout=15).json()


    def print_quote(self, stock=''):    # pragma: no cover
        """Print quote information
            Args:
                stock (str): ticker to fetch

            Returns:
                None
        """

        data = self.get_quote_list(stock, 'symbol,last_trade_price')
        for item in data:
            quote_str = item[0] + ": $" + item[1]
            self.logger.info(quote_str)


    def print_quotes(self, stocks):  # pragma: no cover
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

        return self.get_quote_list(stock, 'ask_price')


    def ask_size(self, stock=''):
        """Get ask size for a stock

            Note:
                queries `quote` endpoint, dict wrapper

            Args:
                stock (str): stock ticker

            Returns:
                (int): ask size
        """

        return self.get_quote_list(stock, 'ask_size')


    def bid_price(self, stock=''):
        """Get bid price for a stock

            Note:
                queries `quote` endpoint, dict wrapper

            Args:
                stock (str): stock ticker

            Returns:
                (float): bid price
        """

        return self.get_quote_list(stock, 'bid_price')


    def bid_size(self, stock=''):
        """Get bid size for a stock

            Note:
                queries `quote` endpoint, dict wrapper

            Args:
                stock (str): stock ticker

            Returns:
                (int): bid size
        """

        return self.get_quote_list(stock, 'bid_size')


    def last_trade_price(self, stock=''):
        """Get last trade price for a stock

            Note:
                queries `quote` endpoint, dict wrapper

            Args:
                stock (str): stock ticker

            Returns:
                (float): last trade price
        """

        return self.get_quote_list(stock, 'last_trade_price')


    def previous_close(self, stock=''):
        """Get previous closing price for a stock

            Note:
                queries `quote` endpoint, dict wrapper

            Args:
                stock (str): stock ticker

            Returns:
                (float): previous closing price
        """

        return self.get_quote_list(stock, 'previous_close')


    def previous_close_date(self, stock=''):
        """Get previous closing date for a stock

            Note:
                queries `quote` endpoint, dict wrapper

            Args:
                stock (str): stock ticker

            Returns:
                (str): previous close date
        """

        return self.get_quote_list(stock, 'previous_close_date')


    def adjusted_previous_close(self, stock=''):
        """Get adjusted previous closing price for a stock

            Note:
                queries `quote` endpoint, dict wrapper

            Args:
                stock (str): stock ticker

            Returns:
                (float): adjusted previous closing price
        """

        return self.get_quote_list(stock, 'adjusted_previous_close')


    def symbol(self, stock=''):
        """Get symbol for a stock

            Note:
                queries `quote` endpoint, dict wrapper

            Args:
                stock (str): stock ticker

            Returns:
                (str): stock symbol
        """

        return self.get_quote_list(stock, 'symbol')


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

        res = self.session.get(endpoints.accounts(), timeout=15)
        res.raise_for_status()  # auth required
        res = res.json()

        return res['results'][0]


    def get_url(self, url):
        """
            Flat wrapper for fetching URL directly
        """

        return self.session.get(url, timeout=15).json()

    def get_popularity(self, stock=''):
        """Get the number of robinhood users who own the given stock

            Args:
                stock (str): stock ticker

            Returns:
                (int): number of users who own the stock
        """
        stock_instrument = self.get_url(self.quote_data(stock)["instrument"])["id"]
        return self.get_url(endpoints.instruments(stock_instrument, "popularity"))["num_open_positions"]

    def get_tickers_by_tag(self, tag=None):
        """Get a list of instruments belonging to a tag

            Args: tag - Tags may include but are not limited to:
                * top-movers
                * etf
                * 100-most-popular
                * mutual-fund
                * finance
                * cap-weighted
                * investment-trust-or-fund

            Returns:
                (List): a list of Ticker strings
        """
        instrument_list = self.get_url(endpoints.tags(tag))["instruments"]
        return [self.get_url(instrument)["symbol"] for instrument in instrument_list]
    
    
    def security_tick(self,instrument):
        """Returns ticker of given instrument
        """

        return self.session.get(instrument).json()['symbol']


    def watchlists(self): 
        """Returns list of securities' symbols that the user has in watchlist
            Returns:
                (:object: `dict`): Non-zero positions
        """
        return self.session.get(endpoints.watchlists() + 'Default/', timeout=15).json()

    ###########################################################################
    #                           GET OPTIONS INFO
    ###########################################################################

    def get_options(self, stock, expiration_dates, option_type):
        """Get a list (chain) of options contracts belonging to a particular stock

            Args: stock ticker (str), list of expiration dates to filter on (YYYY-MM-DD), and whether or not its a 'put' or a 'call' option type (str).

            Returns:
                Options Contracts (List): a list (chain) of contracts for a given underlying equity instrument
        """
        instrument_id = self.get_url(self.quote_data(stock)["instrument"])["id"]
        if type(expiration_dates) == list:
            _expiration_dates_string = ",".join(expiration_dates)
        else:
            _expiration_dates_string = expiration_dates
        chain_id = self.get_url(endpoints.chain(instrument_id))["results"][0]["id"]
        return [contract for contract in self.get_url(endpoints.options(chain_id, _expiration_dates_string, option_type))["results"]]

    @login_required
    def get_option_market_data(self, optionid):
        """Gets a list of market data for a given optionid.

        Args: (str) option id

        Returns: dictionary of options market data.
        """
        market_data = {}
        try:
            market_data = self.get_url(endpoints.market_data(optionid)) or {}
        except requests.exceptions.HTTPError:
            raise RH_exception.InvalidOptionId()
        return market_data


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
        if not stock:   # pragma: no cover
            stock = input("Symbol: ")

        url = str(endpoints.fundamentals(str(stock.upper())))

        #Check for validity of symbol
        try:
            req = self.session.get(url, timeout=15)
            req.raise_for_status()
            data = req.json()
        except requests.exceptions.HTTPError:
            raise RH_exception.InvalidTickerSymbol()


        return data


    def fundamentals(self, stock=''):
        """Wrapper for get_fundamentlals function """

        return self.get_fundamentals(stock)


    ###########################################################################
    #                           PORTFOLIOS DATA
    ###########################################################################

    def portfolios(self):
        """Returns the user's portfolio data """

        req = self.session.get(endpoints.portfolios(), timeout=15)
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

    @login_required
    def order_history(self, orderId=None):
        """Wrapper for portfolios
            Optional Args: add an order ID to retrieve information about a single order.
            Returns:
                (:obj:`dict`): JSON dict from getting orders
        """

        return self.session.get(endpoints.orders(orderId), timeout=15).json()


    def dividends(self):
        """Wrapper for portfolios

            Returns:
                (:obj: `dict`): JSON dict from getting dividends
        """

        return self.session.get(endpoints.dividends(), timeout=15).json()


    ###########################################################################
    #                           POSITIONS DATA
    ###########################################################################

    def positions(self):
        """Returns the user's positions data

            Returns:
                (:object: `dict`): JSON dict from getting positions
        """

        return self.session.get(endpoints.positions(), timeout=15).json()


    def securities_owned(self):
        """Returns list of securities' symbols that the user has shares in

            Returns:
                (:object: `dict`): Non-zero positions
        """

        return self.session.get(endpoints.positions() + '?nonzero=true', timeout=15).json()


    ###########################################################################
    #                               PLACE ORDER
    ###########################################################################
    
    def place_market_buy_order(self,
                               instrument_URL=None,
                               symbol=None,
                               time_in_force=None,
                               quantity=None):
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
        return(self.submit_buy_order(order_type='market',
                                 trigger='immediate',
                                 side='buy',
                                 instrument_URL=instrument_URL,
                                 symbol=symbol,
                                 time_in_force=time_in_force,
                                 quantity=quantity))

    def place_limit_buy_order(self,
                              instrument_URL=None,
                              symbol=None,
                              time_in_force=None,
                              price=None,
                              quantity=None):
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
        return(self.submit_buy_order(order_type='limit',
                                 trigger='immediate',
                                 side='buy',
                                 instrument_URL=instrument_URL,
                                 symbol=symbol,
                                 time_in_force=time_in_force,
                                 price=price,
                                 quantity=quantity))

    def place_stop_loss_buy_order(self,
                                  instrument_URL=None,
                                  symbol=None,
                                  time_in_force=None,
                                  stop_price=None,
                                  quantity=None):
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
        return(self.submit_buy_order(order_type='market',
                                 trigger='stop',
                                 side='buy',
                                 instrument_URL=instrument_URL,
                                 symbol=symbol,
                                 time_in_force=time_in_force,
                                 stop_price=stop_price,
                                 quantity=quantity))

    def place_stop_limit_buy_order(self,
                                   instrument_URL=None,
                                   symbol=None,
                                   time_in_force=None,
                                   stop_price=None,
                                   price=None,
                                   quantity=None):
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
        return(self.submit_buy_order(order_type='limit',
                                 trigger='stop',
                                 side='buy',
                                 instrument_URL=instrument_URL,
                                 symbol=symbol,
                                 time_in_force=time_in_force,
                                 stop_price=stop_price,
                                 price=price,
                                 quantity=quantity))

    def place_market_sell_order(self,
                                instrument_URL=None,
                                symbol=None,
                                time_in_force=None,
                                quantity=None):
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
        return(self.submit_sell_order(order_type='market',
                                 trigger='immediate',
                                 side='sell',
                                 instrument_URL=instrument_URL,
                                 symbol=symbol,
                                 time_in_force=time_in_force,
                                 quantity=quantity))

    def place_limit_sell_order(self,
                               instrument_URL=None,
                               symbol=None,
                               time_in_force=None,
                               price=None,
                               quantity=None):
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
        return(self.submit_sell_order(order_type='limit',
                                 trigger='immediate',
                                 side='sell',
                                 instrument_URL=instrument_URL,
                                 symbol=symbol,
                                 time_in_force=time_in_force,
                                 price=price,
                                 quantity=quantity))

    def place_stop_loss_sell_order(self,
                                   instrument_URL=None,
                                   symbol=None,
                                   time_in_force=None,
                                   stop_price=None,
                                   quantity=None):
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
        return(self.submit_sell_order(order_type='market',
                                 trigger='stop',
                                 side='sell',
                                 instrument_URL=instrument_URL,
                                 symbol=symbol,
                                 time_in_force=time_in_force,
                                 stop_price=stop_price,
                                 quantity=quantity))

    def place_stop_limit_sell_order(self,
                                    instrument_URL=None,
                                    symbol=None,
                                    time_in_force=None,
                                    price=None,
                                    stop_price=None,
                                    quantity=None):
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
        return(self.submit_sell_order(order_type='limit',
                                 trigger='stop',
                                 side='sell',
                                 instrument_URL=instrument_URL,
                                 symbol=symbol,
                                 time_in_force=time_in_force,
                                 stop_price=stop_price,
                                 price=price,
                                 quantity=quantity))

    def submit_sell_order(self,
                     instrument_URL=None,
                     symbol=None,
                     order_type=None,
                     time_in_force=None,
                     trigger=None,
                     price=None,
                     stop_price=None,
                     quantity=None,
                     side=None):
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

        # Used for default price input
        # Price is required, so we use the current bid price if it is not specified
        current_quote = self.get_quote(symbol)
        if (float(current_quote['bid_price']) == 0) or (current_quote['bid_price'] == None):
            current_bid_price = current_quote['last_trade_price']
        else:
            current_bid_price = current_quote['bid_price']

        # Start with some parameter checks. I'm paranoid about $.
        if(instrument_URL is None):
            if(symbol is None):
                raise(ValueError('Neither instrument_URL nor symbol were passed to submit_sell_order'))
            raise(ValueError('Instrument_URL not passed to submit_sell_order'))

        if(symbol is None):
            raise(ValueError('Symbol not passed to submit_sell_order'))

        if(side is None):
            raise(ValueError('Order is neither buy nor sell in call to submit_sell_order'))

        if(order_type is None):
            if(price is None):
                if(stop_price is None):
                    order_type = 'market'
                else:
                    order_type = 'limit'

        symbol = str(symbol).upper()
        order_type = str(order_type).lower()
        time_in_force = str(time_in_force).lower()
        trigger = str(trigger).lower()
        side = str(side).lower()

        if(order_type != 'market') and (order_type != 'limit'):
            raise(ValueError('Invalid order_type in call to submit_sell_order'))

        if(order_type == 'limit'):
            if(price is None):
                raise(ValueError('Limit order has no price in call to submit_sell_order'))
            if(price <= 0):
                raise(ValueError('Price must be positive number in call to submit_sell_order'))

        if(trigger == 'stop'):
            if(stop_price is None):
                raise(ValueError('Stop order has no stop_price in call to submit_sell_order'))
            if(price <= 0):
                raise(ValueError('Stop_price must be positive number in call to submit_sell_order'))

        if(stop_price is not None):
            if(trigger != 'stop'):
                raise(ValueError('Stop price set for non-stop order in call to submit_sell_order'))

        if(price is None):
            if(order_type == 'limit'):
                raise(ValueError('Limit order has no price in call to submit_sell_order'))

        if(price is not None):
            if(order_type.lower() == 'market'):
                raise(ValueError('Market order has price limit in call to submit_sell_order'))
            price = float(price)
        else:
            price = float(current_bid_price) # default to current bid price

        if(quantity is None):
            raise(ValueError('No quantity specified in call to submit_sell_order'))

        quantity = int(quantity)

        if(quantity <= 0):
            raise(ValueError('Quantity must be positive number in call to submit_sell_order'))

        payload = {}

        for field, value in [
                ('account', self.get_account()['url']),
                ('instrument', instrument_URL),
                ('symbol', symbol),
                ('type', order_type),
                ('time_in_force', time_in_force),
                ('trigger', trigger),
                ('price', price),
                ('stop_price', stop_price),
                ('quantity', quantity),
                ('side', side)
            ]:
            if(value is not None):
                payload[field] = value
                
        print(payload)

        try:
            res = self.session.post(endpoints.orders(), data=payload, timeout=15)
            res.raise_for_status()

            return res
        
        except Exception as ex: #sometimes Robinhood asks for another log in when placing an order
            try:
                auth_method()
            except:
                print(ex)
    
    def submit_buy_order(self,
                     instrument_URL=None,
                     symbol=None,
                     order_type=None,
                     time_in_force=None,
                     trigger=None,
                     price=None,
                     stop_price=None,
                     quantity=None,
                     side=None):
        """Submits buy order to Robinhood
       

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
                order_type (str): 'market' or 'limit'
                time_in_force (:enum:`TIME_IN_FORCE`): 'gfd' or 'gtc' (day or
                                                       until cancelled)
                trigger (str): 'immediate' or 'stop' enum
                price (float): The share price you'll accept
                stop_price (float): The price at which the order becomes a
                                    market or limit order
                quantity (int): The number of shares to buy/sell
                side (str): BUY or sell

            Returns:
                (:obj:`requests.request`): result from `orders` put command
        """

        # Used for default price input
        # Price is required, so we use the current ask price if it is not specified
        current_quote = self.get_quote(symbol)
        if (float(current_quote['ask_price']) == 0) or (current_quote['ask_price'] == None):
            current_ask_price = current_quote['last_trade_price']
        else:
            current_ask_price = current_quote['ask_price']

        # Start with some parameter checks. I'm paranoid about $.
        if(instrument_URL is None):
            if(symbol is None):
                raise(ValueError('Neither instrument_URL nor symbol were passed to submit_buy_order'))
            raise(ValueError('Instrument_URL not passed to submit_buy_order'))
            
        if(symbol is None):
            raise(ValueError('Symbol not passed to submit_buy_order'))

        if(side is None):
            raise(ValueError('Order is neither buy nor sell in call to submit_buy_order'))

        if(order_type is None):
            if(price is None):
                if(stop_price is None):
                    order_type = 'market'
                else:
                    order_type = 'limit'

        symbol = str(symbol).upper()
        order_type = str(order_type).lower()
        time_in_force = str(time_in_force).lower()
        trigger = str(trigger).lower()
        side = str(side).lower()

        if(order_type != 'market') and (order_type != 'limit'):
            raise(ValueError('Invalid order_type in call to submit_buy_order'))

        if(order_type == 'limit'):
            if(price is None):
                raise(ValueError('Limit order has no price in call to submit_buy_order'))
            if(price <= 0):
                raise(ValueError('Price must be positive number in call to submit_buy_order'))

        if(trigger == 'stop'):
            if(stop_price is None):
                raise(ValueError('Stop order has no stop_price in call to submit_buy_order'))
            if(price <= 0):
                raise(ValueError('Stop_price must be positive number in call to submit_buy_order'))

        if(stop_price is not None):
            if(trigger != 'stop'):
                raise(ValueError('Stop price set for non-stop order in call to submit_buy_order'))

        if(price is None):
            if(order_type == 'limit'):
                raise(ValueError('Limit order has no price in call to submit_buy_order'))

        if(price is not None):
            if(order_type.lower() == 'market'):
                raise(ValueError('Market order has price limit in call to submit_buy_order'))
            price = float(price)
        else:
            price = float(current_ask_price) # default to current ask price

        if(quantity is None):
            raise(ValueError('No quantity specified in call to submit_buy_order'))

        quantity = int(quantity)

        if(quantity <= 0):
            raise(ValueError('Quantity must be positive number in call to submit_buy_order'))

        payload = {}

        for field, value in [
                ('account', self.get_account()['url']),
                ('instrument', instrument_URL),
                ('symbol', symbol),
                ('type', order_type),
                ('time_in_force', time_in_force),
                ('trigger', trigger),
                ('price', price),
                ('stop_price', stop_price),
                ('quantity', quantity),
                ('side', side)
            ]:
            if(value is not None):
                payload[field] = value

        print(payload)

        try:
            res = self.session.post(endpoints.orders(), data=payload, timeout=15)
            res.raise_for_status()

            return res
        
        except Exception as ex: #sometimes Robinhood asks for another log in when placing an order
            try:
                auth_method()
            except:
                print(ex)
    
  
    def place_order(self,
                    instrument,
                    quantity=1,
                    price=0.0,
                    transaction=None,
                    trigger='immediate',
                    order='market',
                    time_in_force='gfd'):
        """Place an order with Robinhood

            Args:
                instrument (dict): the RH URL and symbol in dict for the instrument to be traded
                quantity (int): quantity of stocks in order
                bid_price (float): price for order
                transaction (:enum:`Transaction`): BUY or SELL enum
                trigger (:enum:`Trigger`): IMMEDIATE or STOP enum
                order (:enum:`Order`): MARKET or LIMIT
                time_in_force (:enum:`TIME_IN_FORCE`): GFD or GTC (day or until cancelled)

            Returns:
                (:obj:`requests.request`): result from `orders` put command
        """

        if isinstance(transaction, str):
            transaction = Transaction(transaction)

        if not price:
            price = float(self.quote_data(instrument['symbol'])['bid_price'])
            
            if (price == 0) or (price == None):
                price = float(self.quote_data(instrument['symbol'])['last_trade_price'])

        payload = {
            'account': self.get_account()['url'],
            'instrument': unquote(instrument['url']),
            'symbol': instrument['symbol'],
            'type': order.lower(),
            'time_in_force': time_in_force.lower(),
            'trigger': trigger,
            'quantity': quantity,
            'side': transaction.name.lower()
        }

        if order.lower() == "stop":
            payload['stop_price'] = float(price)
        else:
            payload['price'] = float(price)

        try:
            res = self.session.post(endpoints.orders(), data=payload, timeout=15)
            res.raise_for_status()

            return res
        
        except Exception as ex: #sometimes Robinhood asks for another log in when placing an order
            try:
                auth_method()
            except:
                print(ex)

    def place_buy_order(self,
                        instrument,
                        quantity,
                        ask_price=0.0):
        """Wrapper for placing buy orders

            Args:
                instrument (dict): the RH URL and symbol in dict for the instrument to be traded
                quantity (int): quantity of stocks in order
                ask_price (float): price for order (OPTIONAL! If not given, ask_price is automatic.)

            Returns:
                (:obj:`requests.request`): result from `orders` put command

        """

        if not ask_price:
            ask_price = float(self.quote_data(instrument['symbol'])['ask_price'])
            
            if (ask_price == 0) or (ask_price == None):
                ask_price = float(self.quote_data(instrument['symbol'])['last_trade_price'])
            
        transaction = Transaction.BUY

        return self.place_order(instrument, quantity, ask_price, transaction)


    def place_sell_order(self,
                         instrument,
                         quantity,
                         bid_price=0.0):
        """Wrapper for placing sell orders

            Args:
                instrument (dict): the RH URL and symbol in dict for the instrument to be traded
                quantity (int): quantity of stocks in order
                bid_price (float): price for order (OPTIONAL! If not given, bid_price is automatic.)

            Returns:
                (:obj:`requests.request`): result from `orders` put command
        """
        if not bid_price:
            bid_price = float(self.quote_data(instrument['symbol'])['bid_price'])
            
            if (bid_price == 0) or (bid_price == None):
                bid_price = float(self.quote_data(instrument['symbol'])['last_trade_price'])
            
        transaction = Transaction.SELL

        return self.place_order(instrument, quantity, bid_price, transaction)


    ##############################
    #                          CANCEL ORDER
    ##############################

    def cancel_order(
            self,
            order_id):
        """
        Cancels specified order and returns the response (results from `orders` command).
        If order cannot be cancelled, `None` is returned.
        Args:
            order_id (str or dict): Order ID string that is to be cancelled or open order dict returned from
            order get.
        Returns:
            (:obj:`requests.request`): result from `orders` put command
        """
        if isinstance(order_id, str):
            try:
                order = self.session.get(endpoints.orders() + order_id, timeout=15).json()
            except (requests.exceptions.HTTPError) as err_msg:
                raise ValueError('Failed to get Order for ID: ' + order_id
                    + '\n Error message: '+ repr(err_msg))

            if order.get('cancel') is not None:
                try:
                    res = self.session.post(order['cancel'], timeout=15)
                    res.raise_for_status()
                    return res
                except (requests.exceptions.HTTPError) as err_msg:
                    try: #sometimes Robinhood asks for another log in when placing an order
                        res = self.session.post(order['cancel'], headers=self.headers, timeout=15)
                        res.raise_for_status()
                        return res
                    except (requests.exceptions.HTTPError) as err_msg:
                        raise ValueError('Failed to cancel order ID: ' + order_id
                             + '\n Error message: '+ repr(err_msg))
                        return None

        if isinstance(order_id, dict):
            order_id = order_id['id']
            try:
                order = self.session.get(endpoints.orders() + order_id, timeout=15).json()
            except (requests.exceptions.HTTPError) as err_msg:
                raise ValueError('Failed to get Order for ID: ' + order_id
                    + '\n Error message: '+ repr(err_msg))

            if order.get('cancel') is not None:
                try:
                    res = self.session.post(order['cancel'], timeout=15)
                    res.raise_for_status()
                    return res
                except (requests.exceptions.HTTPError) as err_msg:
                    try: #sometimes Robinhood asks for another log in when placing an order
                        res = self.session.post(order['cancel'], headers=self.headers, timeout=15)
                        res.raise_for_status()
                        return res
                    except (requests.exceptions.HTTPError) as err_msg:
                        raise ValueError('Failed to cancel order ID: ' + order_id
                             + '\n Error message: '+ repr(err_msg))
                        return None
                    
        elif not isinstance(order_id, str) or not isinstance(order_id, dict):
            raise ValueError('Cancelling orders requires a valid order_id string or open order dictionary')


        # Order type cannot be cancelled without a valid cancel link
        else:
            raise ValueError('Unable to cancel order ID: ' + order_id)
