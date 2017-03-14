
import getpass
import logging
from enum import Enum
#from urllib.request import getproxies
#import urllib.request, urllib.parse, urllib.error

import requests
import six
from six.moves.urllib.parse import unquote
from six.moves.urllib.request import getproxies
from six.moves import input

class Bounds(Enum):
    """enum for bounds in `historicals` endpoint"""
    REGULAR = 'regular'
    EXTENDED = 'extended'

class Robinhood:

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
        "margin_upgrades": "https://api.robinhood.com/margin/upgrades/",
        "markets": "https://api.robinhood.com/markets/",
        "notifications": "https://api.robinhood.com/notifications/",
        "orders": "https://api.robinhood.com/orders/",
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

    logger = logging.getLogger('Robinhood').addHandler(logging.NullHandler())

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

    def login_prompt(self):
        """Prompts user for username and password and calls login()."""
        username = input("Username: ")
        password = getpass.getpass()
        return self.login(username=username, password=password)

    def login(
            self,
            username,
            password
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
        #data = urllib.parse.urlencode({"password" : self.password, "username" : self.username})
        params = {
            'password': self.password,
            'username': self.username
        }
        #res = self.session.post(self.endpoints['login'], data=data)
        res = self.session.post(self.endpoints['login'], params=params)
        res = res.json()
        try:
            self.auth_token = res['token']
        except KeyError:
            return False
        self.headers['Authorization'] = 'Token ' + self.auth_token
        return True

    def logout(self):
        """logout from Robinhood

        Returns:
            (:obj:`requests.request`) result from logout endpoint

        """
        self.headers['Authorization'] = None
        self.auth_token = None
        return self.session.post(self.endpoints['logout'])

    ##############################
    #GET DATA
    ##############################

    def investment_profile(self):
        """fetch investment_profile"""
        self.session.get(self.endpoints['investment_profile'])

    def instruments(self, stock):
        """fetch instruments endpoint

        Args:
            stock (str): stock ticker

        Returns:
            (:obj:`dict`): JSON contents from `instruments` endpoint

        """
        params = {
            'query': stock.upper()
        }
        res = self.session.get(
            self.endpoints['instruments'],
            params=params
        )
        res = res.json()
        return res['results']

    def quote_data(self, stock=''):
        """fetch stock quote (prompt if blank)

        Args:
            stock (str): stock ticker, prompt if blank

        Returns:
            (:obj:`dict`): JSON contents from `quotes` endpoint

        """
        #Prompt for stock if not entered
        if not stock:
            stock = input("Symbol: ")
        url = str(self.endpoints['quotes']) + str(stock) + "/"
        #Check for validity of symbol
        try:
            req = requests.get(url)
            req.raise_for_status()
            data = req.json()
        except requests.exceptions.HTTPError:
            raise NameError('Invalid Symbol: ' + stock) #TODO: custom exception

        return data

    def get_quote(self, stock=''):
        """wrapper for quote_data"""
        data = self.quote_data(stock)
        return data["symbol"]

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
            bounds can be 'regular' for regular hours or 'extended' for extended hours
        Args:
            stock (str): stock ticker
            interval (str): resolution of data
            span (str): length of data
            bounds (:enum:`Bounds`, optional): ??

        Returns:
            (:obj:`dict`) values returned from `historicals` endpoint

        """
        # Valid combination
        # interval = 5minute | 10minute + span = day, week
        # interval = day + span = year
        # interval = week
        # bounds can be 'regular' for regular hours or 'extended' for extended hours
        params = {
            'symbols': ','.join(stock).upper,
            'interval': interval,
            'span': span,
            'bounds': bounds.name.lower()
        }
        res = self.session.get(self.endpoints['historicals'], params=params)
        return res.json()

    def get_news(self, symbol):
        return self.session.get(self.endpoints['news']+symbol.upper()+"/").json()

    def print_quote(self, stock=None):
        data = self.quote_data(stock)
        print((data["symbol"] + ": $" + data["last_trade_price"]))

    def print_quotes(self, stocks):
        for stock in stocks:
            self.print_quote(stock)

    def ask_price(self, stock=None):
        return self.quote_data(stock)['ask_price']

    def ask_size(self, stock=None):
        return self.quote_data(stock)['ask_size']

    def bid_price(self, stock=None):
        return self.quote_data(stock)['bid_price']

    def bid_size(self, stock=None):
        return self.quote_data(stock)['bid_size']

    def last_trade_price(self, stock=None):
        return self.quote_data(stock)['last_trade_price']

    def previous_close(self, stock=None):
        return self.quote_data(stock)['previous_close']

    def previous_close_date(self, stock=None):
        return self.quote_data(stock)['previous_close_date']

    def adjusted_previous_close(self, stock=None):
        return self.quote_data(stock)['adjusted_previous_close']

    def symbol(self, stock=None):
        return self.quote_data(stock)['symbol']

    def last_updated_at(self, stock=None):
        return self.quote_data(stock)['updated_at']

    def get_account(self):
        res = self.session.get(self.endpoints['accounts'])
        res = res.json()
        return res['results'][0]

    def get_fundamentals(self, stock=''):
        #Prompt for stock if not entered
        if not stock:
            stock = input("Symbol: ")

        url = str(self.endpoints['fundamentals']) + str(stock.upper()) + "/"
        #Check for validity of symbol
        try:
            req = requests.get(url)
            req.raise_for_status()
            data = req.json()
        except requests.exceptions.HTTPError:
            raise NameError('Invalid Symbol: ' + stock)

        return data
        #try:
        #    res = json.loads((urllib.request.urlopen(url)).read().decode('utf-8'));
        #    if len(res) > 0:
        #        return res;
        #    else:
        #        raise NameError("Invalid Symbol: " + stock);
        #except (ValueError):
        #    raise NameError("Invalid Symbol: " + stock);

    def fundamentals(self, stock=None):
        return self.get_fundamentals(stock)

    def get_url(self,url):
        return self.session.get(url).json()

    ##############################
    # PORTFOLIOS DATA
    ##############################

    def portfolios(self):
        """Returns the user's portfolio data."""
        return self.session.get(self.endpoints['portfolios']).json()['results'][0]

    def adjusted_equity_previous_close(self):
        return float(self.portfolios()['adjusted_equity_previous_close'])

    def equity(self):
        return float(self.portfolios()['equity'])

    def equity_previous_close(self):
        return float(self.portfolios()['equity_previous_close'])

    def excess_margin(self):
        return float(self.portfolios()['excess_margin'])

    def extended_hours_equity(self):
        return float(self.portfolios()['extended_hours_equity'])

    def extended_hours_market_value(self):
        return float(self.portfolios()['extended_hours_market_value'])

    def last_core_equity(self):
        return float(self.portfolios()['last_core_equity'])

    def last_core_market_value(self):
        return float(self.portfolios()['last_core_market_value'])

    def market_value(self):
        return float(self.portfolios()['market_value'])

    def order_history(self):
        return self.session.get(self.endpoints['orders']).json()

    def dividends(self):
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
        positions = self.positions()
        securities = []
        for position in positions['results']:
            quantity = float(position['quantity'])
            if quantity > 0:
                securities.append(self.session.get(position['instrument']).json()['symbol'])
        return securities

    ##############################
    #PLACE ORDER
    ##############################

    def place_order(
            self,
            instrument,
            quantity=1,
            bid_price=0.0,
            transaction=None
        ):
        if not bid_price:
            bid_price = self.quote_data(instrument['symbol'])['bid_price']
        payload = {
            'account': self.get_account()['url'],
            'instrument': unquote(instrument['url']),
            'price': float(bid_price),
            'quantity': quantity,
            'side': transaction,
            'symbol': instrument['symbol'],
            'time_in_force': 'gfd',
            'trigger': 'immediate',
            'type': 'market'
        }
        #data = 'account=%s&instrument=%s&price=%f&quantity=%d&side=%s&symbol=%s#&time_in_force=gfd&trigger=immediate&type=market' % (
        #    self.get_account()['url'],
        #    urllib.parse.unquote(instrument['url']),
        #    float(bid_price),
        #    quantity,
        #    transaction,
        #    instrument['symbol']
        #)
        res = self.session.post(
            self.endpoints['orders'],
            params=payload
        )
        return res

    def place_buy_order(
            self,
            instrument,
            quantity,
            bid_price=0.0
        ):
        transaction = "buy"
        return self.place_order(instrument, quantity, bid_price, transaction)

    def place_sell_order(
            self,
            instrument,
            quantity,
            bid_price=0.0
        ):
        transaction = "sell"
        return self.place_order(instrument, quantity, bid_price, transaction)
