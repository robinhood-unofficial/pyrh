"""robinhood.py: a collection of utilities for working with Robinhood's Private API."""

from enum import Enum
from urllib.parse import unquote

import dateutil
import requests
from yarl import URL

from pyrh import urls
from pyrh.exceptions import InvalidTickerSymbol
from pyrh.models import (
    InstrumentManager,
    PortfolioSchema,
    SessionManager,
    SessionManagerSchema,
)

# TODO: re-enable InvalidOptionId when broken endpoint function below is fixed


class Bounds(Enum):
    """Enum for bounds in `historicals` endpoint."""

    REGULAR = "regular"
    EXTENDED = "extended"


class Transaction(Enum):
    """Enum for buy/sell orders."""

    BUY = "buy"
    SELL = "sell"


class Robinhood(InstrumentManager, SessionManager):
    """Wrapper class for fetching/parsing Robinhood endpoints.

    Please see :py:class:`pyrh.models.sessionmanager.SessionManager` for login functionality.

    Provides a global convenience wrapper for the following manager objects:

        * InstrumentManager
        * TODO: Add to this list

    """

    ###########################################################################
    #                               GET DATA                                  #
    ###########################################################################

    def user(self):
        return self.get(urls.USER)

    def investment_profile(self):
        """Fetch investment_profile."""
        return self.get(urls.INVESTMENT_PROFILE)

    def quote_data(self, stock=""):
        """Fetch stock quote.

        Args:
            stock (str or dict): stock ticker symbol or stock instrument

        Returns:
            (:obj:`dict`): JSON contents from `quotes` endpoint

        """

        if isinstance(stock, dict):
            if "symbol" in stock.keys():
                url = str(urls.QUOTES) + stock["symbol"] + "/"
        elif isinstance(stock, str):
            url = str(urls.QUOTES) + stock + "/"
        else:
            raise InvalidTickerSymbol()

        # Check for validity of symbol
        try:
            data = self.get(url)
        except requests.exceptions.HTTPError:
            raise InvalidTickerSymbol()

        return data

    # We will keep for compatibility until next major release
    def quotes_data(self, stocks):
        """Fetch quote for multiple stocks, in one single Robinhood API call.

        Args:
            stocks (list<str>): stock tickers

        Returns:
            (:obj:`list` of :obj:`dict`): List of JSON contents from `quotes` \
                endpoint, in the same order of input args. If any ticker is \
                invalid, a None will occur at that position.

        """

        url = str(urls.QUOTES) + "?symbols=" + ",".join(stocks)

        try:
            data = self.get(url)
        except requests.exceptions.HTTPError:
            raise InvalidTickerSymbol()

        return data["results"]

    def get_quote_list(self, stock="", key=""):
        """Returns multiple stock info and keys from quote_data (prompt if blank)

        Args:
            stock (str): stock ticker (or tickers separated by a comma)
            , prompt if blank
            key (str): key attributes that the function should return

        Returns:
            (:obj:`list`): Returns values from each stock or empty list
                           if none of the stocks were valid

        """

        # Creates a tuple containing the information we want to retrieve
        def append_stock(stock):
            keys = key.split(",")
            myStr = ""
            for item in keys:
                myStr += f"{stock[item]},"

            return myStr.split(",")

        # Prompt for stock if not entered
        if not stock:  # pragma: no cover
            stock = input("Symbol: ")

        data = self.quote_data(stock)
        res = []

        # Handles the case of multple tickers
        if stock.find(",") != -1:
            for stock in data["results"]:
                if stock is None:
                    continue
                res.append(append_stock(stock))

        else:
            res.append(append_stock(data))

        return res

    def get_quote(self, stock=""):
        """Wrapper for quote_data."""

        data = self.quote_data(stock)
        return data

    def get_stock_marketdata(self, instruments):
        info = self.get_url(
            urls.build_market_data() + "quotes/?instruments=" + ",".join(instruments)
        )
        return info["results"]

    def get_historical_quotes(self, stock, interval, span, bounds=Bounds.REGULAR):
        self.endpoint_ = """Fetch historical data for stock.

        Note: valid interval/span configs
            interval = 5minute | 10minute + span = day, week
            interval = day + span = year
            interval = week
            TODO: NEEDS TESTS

        Args:
            stock (str): stock ticker
            interval (str): resolution of data
            span (str): length of data
            bounds (:obj:`Bounds`, optional): 'extended' or 'regular' trading hours

        Returns:
            (:obj:`dict`) values returned from `historicals` endpoint

        """
        if type(stock) is str:
            stock = [stock]

        if isinstance(bounds, str):  # recast to Enum
            bounds = Bounds(bounds)

        historicals = urls.HISTORICALS.with_query(
            [
                ("symbols", ",".join(stock).upper()),
                ("interval", interval),
                ("span", span),
                ("bounds", bounds.name.lower()),
            ]
        )

        return self.get(historicals)

    def get_news(self, stock):
        """Fetch news endpoint.

        Args:
            stock (str): stock ticker

        Returns:
            (:obj:`dict`) values returned from `news` endpoint

        """

        return self.get(urls.build_news(stock.upper()))

    def get_watchlists(self):
        """Fetch watchlists endpoint and queries for
        each instrumented result aka stock details returned from the watchlist

        Returns:
            (:obj:`dict`): values returned from `watchlists` and `instrument` endpoints
        """

        res = []
        watchlist = self.get(urls.WATCHLISTS)
        if watchlist and "results" in watchlist:
            data = self.get(watchlist["results"][0]["url"])
            for rec in data["results"]:
                res.append(self.get(rec["instrument"]))

        return res

    def print_quote(self, stock=""):  # pragma: no cover
        """Print quote information.

        Args:
            stock (str): ticker to fetch

        Returns:
            None

        """

        data = self.get_quote_list(stock, "symbol,last_trade_price")
        for item in data:
            quote_str = item[0] + ": $" + item[1]
            print(quote_str)

    def print_quotes(self, stocks):  # pragma: no cover
        """Print a collection of stocks.

        Args:
            stocks (:obj:`list`): list of stocks to pirnt

        Returns:
            None

        """

        if stocks is None:
            return

        for stock in stocks:
            self.print_quote(stock)

    def ask_price(self, stock=""):
        """Get asking price for a stock.

        Note:
            queries `quote` endpoint, dict wrapper

        Args:
            stock (str): stock ticker

        Returns:
            (float): ask price

        """

        return self.get_quote_list(stock, "ask_price")

    def ask_size(self, stock=""):
        """Get ask size for a stock.

        Note:
            queries `quote` endpoint, dict wrapper

        Args:
            stock (str): stock ticker

        Returns:
            (int): ask size

        """

        return self.get_quote_list(stock, "ask_size")

    def bid_price(self, stock=""):
        """Get bid price for a stock.

        Note:
            queries `quote` endpoint, dict wrapper

        Args:
            stock (str): stock ticker

        Returns:
            (float): bid price

        """

        return self.get_quote_list(stock, "bid_price")

    def bid_size(self, stock=""):
        """Get bid size for a stock.

        Note:
            queries `quote` endpoint, dict wrapper

        Args:
            stock (str): stock ticker

        Returns:
            (int): bid size

        """

        return self.get_quote_list(stock, "bid_size")

    def last_trade_price(self, stock=""):
        """Get last trade price for a stock

        Note:
            queries `quote` endpoint, dict wrapper

        Args:
            stock (str): stock ticker

        Returns:
            (float): last trade price

        """

        return self.get_quote_list(stock, "last_trade_price")

    def previous_close(self, stock=""):
        """Get previous closing price for a stock.

        Note:
            queries `quote` endpoint, dict wrapper

        Args:
            stock (str): stock ticker

        Returns:
            (float): previous closing price

        """

        return self.get_quote_list(stock, "previous_close")

    def previous_close_date(self, stock=""):
        """Get previous closing date for a stock.

        Note:
            queries `quote` endpoint, dict wrapper

        Args:
            stock (str): stock ticker

        Returns:
            (str): previous close date

        """

        return self.get_quote_list(stock, "previous_close_date")

    def adjusted_previous_close(self, stock=""):
        """Get adjusted previous closing price for a stock.

        Note:
            queries `quote` endpoint, dict wrapper

        Args:
            stock (str): stock ticker

        Returns:
            (float): adjusted previous closing price

        """

        return self.get_quote_list(stock, "adjusted_previous_close")

    def symbol(self, stock=""):
        """Get symbol for a stock.

        Note:
            queries `quote` endpoint, dict wrapper

        Args:
            stock (str): stock ticker

        Returns:
            (str): stock symbol

        """

        return self.get_quote_list(stock, "symbol")

    def last_updated_at(self, stock=""):
        """Get last update datetime.

        Note:
            queries `quote` endpoint, dict wrapper

        Args:
            stock (str): stock ticker

        Returns:
            (str): last update datetime
        """

        return self.get_quote_list(stock, "last_updated_at")

    def last_updated_at_datetime(self, stock=""):
        """Get last updated datetime.

        Note:
            queries `quote` endpoint, dict wrapper
            `self.last_updated_at` returns time as `str` in format:
            'YYYY-MM-ddTHH:mm:ss:000Z'

        Args:
            stock (str): stock ticker

        Returns:
            (datetime): last update datetime

        """

        # Will be in format: 'YYYY-MM-ddTHH:mm:ss:000Z'
        datetime_string = self.last_updated_at(stock)
        result = dateutil.parser.parse(datetime_string)

        return result

    def get_account(self):
        """Fetch account information.

        Returns:
            (:obj:`dict`): `accounts` endpoint payload

        """

        res = self.get(urls.ACCOUNTS)

        return res["results"][0]

    def get_url(self, url):
        """Flat wrapper for fetching URL directly/"""

        return self.get(url)

    def get_popularity(self, stock=""):
        """Get the number of robinhood users who own the given stock

        Args:
            stock (str): stock ticker

        Returns:
            (int): number of users who own the stock

        """
        stock_instrument = self.get_url(self.quote_data(stock)["instrument"])["id"]
        return self.get_url(urls.build_instruments(stock_instrument, "popularity"))[
            "num_open_positions"
        ]

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
        instrument_list = self.get_url(urls.build_tags(tag))["instruments"]
        return [self.get_url(instrument)["symbol"] for instrument in instrument_list]

    ###########################################################################
    #                           GET OPTIONS INFO                              #
    ###########################################################################

    def get_options(self, stock, expiration_dates, option_type):
        """Get a list (chain) of options contracts belonging to a particular stock

        Args: stock ticker (str), list of expiration dates to filter on
            (YYYY-MM-DD), and whether or not its a 'put' or a 'call' option type
            (str).

        Returns:
            Options Contracts (List): a list (chain) of contracts for a given \
            underlying equity instrument

        """
        instrument_id = self.get_url(self.quote_data(stock)["instrument"])["id"]
        if type(expiration_dates) == list:
            _expiration_dates_string = ",".join(expiration_dates)
        else:
            _expiration_dates_string = expiration_dates
        chain_id = self.get_url(urls.build_chain(instrument_id))["results"][0]["id"]
        return [
            contract
            for contract in self.get_url(
                urls.options(chain_id, _expiration_dates_string, option_type)
            )["results"]
        ]

    # TODO: the endpoint `option_market_data` doesn't exist
    # def get_option_market_data(self, optionid):
    #     """Gets a list of market data for a given optionid.
    #
    #     Args: (str) option id
    #
    #     Returns: dictionary of options market data.
    #
    #     """
    #     market_data = {}
    #     try:
    #         market_data = self.get_url(endpoints.option_market_data(optionid)) or {}
    #     except requests.exceptions.HTTPError:
    #         raise InvalidOptionId()
    #     return market_data

    def options_owned(self):
        options = self.get_url(urls.OPTIONS_BASE.join(URL("positions/?nonzero=true")))
        options = options["results"]
        return options

    def get_option_marketdata(self, option_id):
        info = self.get_url(urls.MARKET_DATA_BASE.join(URL(f"options/{option_id}/")))
        return info

    def get_option_chainid(self, symbol):
        stock_info = self.get_url(urls.INSTRUMENTS_BASE.with_query(symbol=symbol))
        instrument_id = stock_info["results"][0]["id"]
        url = urls.OPTIONS_BASE.join(URL("chains/"))
        chains = self.get_url(url.with_query(equity_instrument_ids=instrument_id))
        chains = chains["results"]
        chain_id = None

        for chain in chains:
            if chain["can_open_position"]:
                chain_id = chain["id"]

        return chain_id

    def get_option_quote(self, symbol, strike, expiry, otype, state="active"):
        url = urls.OPTIONS_BASE.join(URL("instruments/"))
        params = {
            "chain_symbol": symbol,
            "strike_price": strike,
            "expiration_dates": expiry,
            "type": otype,
            "state": state,
        }
        # symbol, strike, expiry, otype should uniquely define an option
        results = self.get_url(url.with_query(**params)).get("results")
        if not results:
            return
        else:
            option_id = results[0]["id"]
            result = self.get_option_marketdata(option_id)
            params["ask"] = "{} x {}".format(result["ask_size"], result["ask_price"])
            params["bid"] = "{} x {}".format(result["bid_size"], result["bid_price"])
            return params

    ###########################################################################
    #                           GET FUNDAMENTALS
    ###########################################################################

    def get_fundamentals(self, stock=""):
        """Find stock fundamentals data

        Args:
            (str): stock ticker

        Returns:
            (:obj:`dict`): contents of `fundamentals` endpoint

        """

        # Prompt for stock if not entered
        if not stock:  # pragma: no cover
            stock = input("Symbol: ")

        url = str(urls.build_fundamentals(str(stock.upper())))

        # Check for validity of symbol
        try:
            data = self.get(url)
        except requests.exceptions.HTTPError:
            raise InvalidTickerSymbol()

        return data

    def fundamentals(self, stock=""):
        """Wrapper for get_fundamentlals function"""

        return self.get_fundamentals(stock)

    ###########################################################################
    #                           PORTFOLIOS DATA
    ###########################################################################

    def portfolio(self):
        """Returns the user's portfolio data"""

        return self.get(urls.PORTFOLIOS, schema=PortfolioSchema())

    def order_history(self, orderId=None):
        """Wrapper for portfolios

        Optional Args: add an order ID to retrieve information about a single order.

        Returns:
            (:obj:`dict`): JSON dict from getting orders

        """

        return self.get(urls.build_orders(orderId))

    def dividends(self):
        """Wrapper for portfolios

        Returns:
            (:obj: `dict`): JSON dict from getting dividends

        """

        return self.get(urls.DIVIDENDS)

    ###########################################################################
    #                           POSITIONS DATA
    ###########################################################################

    def positions(self):
        """Returns the user's positions data

        Returns:
            (:object: `dict`): JSON dict from getting positions

        """

        return self.get(urls.POSITIONS)

    def securities_owned(self):
        """Returns list of securities' symbols that the user has shares in

        Returns:
            (:object: `dict`): Non-zero positions

        """

        return self.get(str(urls.POSITIONS) + "?nonzero=true")

    ###########################################################################
    #                               PLACE ORDER
    ###########################################################################

    def place_market_buy_order(
        self, instrument_URL=None, symbol=None, time_in_force=None, quantity=None
    ):
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
        return self.submit_buy_order(
            order_type="market",
            trigger="immediate",
            side="buy",
            instrument_URL=instrument_URL,
            symbol=symbol,
            time_in_force=time_in_force,
            quantity=quantity,
        )

    def place_limit_buy_order(
        self,
        instrument_URL=None,
        symbol=None,
        time_in_force=None,
        price=None,
        quantity=None,
    ):
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
        return self.submit_buy_order(
            order_type="limit",
            trigger="immediate",
            side="buy",
            instrument_URL=instrument_URL,
            symbol=symbol,
            time_in_force=time_in_force,
            price=price,
            quantity=quantity,
        )

    def place_stop_loss_buy_order(
        self,
        instrument_URL=None,
        symbol=None,
        time_in_force=None,
        stop_price=None,
        quantity=None,
    ):
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
        return self.submit_buy_order(
            order_type="market",
            trigger="stop",
            side="buy",
            instrument_URL=instrument_URL,
            symbol=symbol,
            time_in_force=time_in_force,
            stop_price=stop_price,
            quantity=quantity,
        )

    def place_stop_limit_buy_order(
        self,
        instrument_URL=None,
        symbol=None,
        time_in_force=None,
        stop_price=None,
        price=None,
        quantity=None,
    ):
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
        return self.submit_buy_order(
            order_type="limit",
            trigger="stop",
            side="buy",
            instrument_URL=instrument_URL,
            symbol=symbol,
            time_in_force=time_in_force,
            stop_price=stop_price,
            price=price,
            quantity=quantity,
        )

    def place_market_sell_order(
        self, instrument_URL=None, symbol=None, time_in_force=None, quantity=None
    ):
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
        return self.submit_sell_order(
            order_type="market",
            trigger="immediate",
            side="sell",
            instrument_URL=instrument_URL,
            symbol=symbol,
            time_in_force=time_in_force,
            quantity=quantity,
        )

    def place_limit_sell_order(
        self,
        instrument_URL=None,
        symbol=None,
        time_in_force=None,
        price=None,
        quantity=None,
    ):
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
        return self.submit_sell_order(
            order_type="limit",
            trigger="immediate",
            side="sell",
            instrument_URL=instrument_URL,
            symbol=symbol,
            time_in_force=time_in_force,
            price=price,
            quantity=quantity,
        )

    def place_stop_loss_sell_order(
        self,
        instrument_URL=None,
        symbol=None,
        time_in_force=None,
        stop_price=None,
        quantity=None,
    ):
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
        return self.submit_sell_order(
            order_type="market",
            trigger="stop",
            side="sell",
            instrument_URL=instrument_URL,
            symbol=symbol,
            time_in_force=time_in_force,
            stop_price=stop_price,
            quantity=quantity,
        )

    def place_stop_limit_sell_order(
        self,
        instrument_URL=None,
        symbol=None,
        time_in_force=None,
        price=None,
        stop_price=None,
        quantity=None,
    ):
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
        return self.submit_sell_order(
            order_type="limit",
            trigger="stop",
            side="sell",
            instrument_URL=instrument_URL,
            symbol=symbol,
            time_in_force=time_in_force,
            stop_price=stop_price,
            price=price,
            quantity=quantity,
        )

    # TODO: fix the function complexity
    def submit_sell_order(  # noqa: C901
        self,
        instrument_URL=None,
        symbol=None,
        order_type=None,
        time_in_force=None,
        trigger=None,
        price=None,
        stop_price=None,
        quantity=None,
        side=None,
    ):
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
            time_in_force (:obj:`TIME_IN_FORCE`): GFD or GTC (day or
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
        if (current_quote["bid_price"] == 0) or (current_quote["bid_price"] is None):
            current_bid_price = current_quote["last_trade_price"]
        else:
            current_bid_price = current_quote["bid_price"]

        # Start with some parameter checks. I'm paranoid about $.
        if instrument_URL is None:
            if symbol is None:
                raise (
                    ValueError(
                        "Neither instrument_URL nor symbol were passed to "
                        "submit_sell_order"
                    )
                )
            raise (ValueError("Instrument_URL not passed to submit_sell_order"))

        if symbol is None:
            raise (ValueError("Symbol not passed to submit_sell_order"))

        if side is None:
            raise (
                ValueError("Order is neither buy nor sell in call to submit_sell_order")
            )

        if order_type is None:
            if price is None:
                if stop_price is None:
                    order_type = "market"
                else:
                    order_type = "limit"

        symbol = str(symbol).upper()
        order_type = str(order_type).lower()
        time_in_force = str(time_in_force).lower()
        trigger = str(trigger).lower()
        side = str(side).lower()

        if (order_type != "market") and (order_type != "limit"):
            raise (ValueError("Invalid order_type in call to submit_sell_order"))

        if order_type == "limit":
            if price is None:
                raise (
                    ValueError("Limit order has no price in call to submit_sell_order")
                )
            if price <= 0:
                raise (
                    ValueError(
                        "Price must be positive number in call to submit_sell_order"
                    )
                )

        if trigger == "stop":
            if stop_price is None:
                raise (
                    ValueError(
                        "Stop order has no stop_price in call to submit_sell_order"
                    )
                )
            if price <= 0:
                raise (
                    ValueError(
                        "Stop_price must be positive number in call to "
                        "submit_sell_order"
                    )
                )

        if stop_price is not None:
            if trigger != "stop":
                raise (
                    ValueError(
                        "Stop price set for non-stop order in call to submit_sell_order"
                    )
                )

        if price is None:
            if order_type == "limit":
                raise (
                    ValueError("Limit order has no price in call to submit_sell_order")
                )

        if price is not None:
            if order_type.lower() == "market":
                raise (
                    ValueError(
                        "Market order has price limit in call to submit_sell_order"
                    )
                )
            price = float(price)
        else:
            price = current_bid_price  # default to current bid price

        if quantity is None:
            raise (ValueError("No quantity specified in call to submit_sell_order"))

        quantity = int(quantity)

        if quantity <= 0:
            raise (
                ValueError(
                    "Quantity must be positive number in call to submit_sell_order"
                )
            )

        payload = {}

        for field, value in [
            ("account", self.get_account()["url"]),
            ("instrument", instrument_URL),
            ("symbol", symbol),
            ("type", order_type),
            ("time_in_force", time_in_force),
            ("trigger", trigger),
            ("price", price),
            ("stop_price", stop_price),
            ("quantity", quantity),
            ("side", side),
        ]:
            if value is not None:
                payload[field] = value

        res = self.post(urls.build_orders(), data=payload)
        return res

    # TODO: Fix function complexity
    def submit_buy_order(  # noqa: C901
        self,
        instrument_URL=None,
        symbol=None,
        order_type=None,
        time_in_force=None,
        trigger=None,
        price=None,
        stop_price=None,
        quantity=None,
        side=None,
    ):
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
            time_in_force (:obj:`TIME_IN_FORCE`): 'gfd' or 'gtc' (day or
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
        if (current_quote["ask_price"] == 0) or (current_quote["ask_price"] is None):
            current_ask_price = current_quote["last_trade_price"]
        else:
            current_ask_price = current_quote["ask_price"]

        # Start with some parameter checks. I'm paranoid about $.
        if instrument_URL is None:
            if symbol is None:
                raise (
                    ValueError(
                        "Neither instrument_URL nor symbol were passed to "
                        "submit_buy_order"
                    )
                )
            raise (ValueError("Instrument_URL not passed to submit_buy_order"))

        if symbol is None:
            raise (ValueError("Symbol not passed to submit_buy_order"))

        if side is None:
            raise (
                ValueError("Order is neither buy nor sell in call to submit_buy_order")
            )

        if order_type is None:
            if price is None:
                if stop_price is None:
                    order_type = "market"
                else:
                    order_type = "limit"

        symbol = str(symbol).upper()
        order_type = str(order_type).lower()
        time_in_force = str(time_in_force).lower()
        trigger = str(trigger).lower()
        side = str(side).lower()

        if (order_type != "market") and (order_type != "limit"):
            raise (ValueError("Invalid order_type in call to submit_buy_order"))

        if order_type == "limit":
            if price is None:
                raise (
                    ValueError("Limit order has no price in call to submit_buy_order")
                )
            if price <= 0:
                raise (
                    ValueError(
                        "Price must be positive number in call to submit_buy_order"
                    )
                )

        if trigger == "stop":
            if stop_price is None:
                raise (
                    ValueError(
                        "Stop order has no stop_price in call to submit_buy_order"
                    )
                )
            if price <= 0:
                raise (
                    ValueError(
                        "Stop_price must be positive number in call to submit_buy_order"
                    )
                )

        if stop_price is not None:
            if trigger != "stop":
                raise (
                    ValueError(
                        "Stop price set for non-stop order in call to submit_buy_order"
                    )
                )

        if price is None:
            if order_type == "limit":
                raise (
                    ValueError("Limit order has no price in call to submit_buy_order")
                )

        if price is not None:
            if order_type.lower() == "market":
                raise (
                    ValueError(
                        "Market order has price limit in call to submit_buy_order"
                    )
                )
            price = float(price)
        else:
            price = current_ask_price  # default to current ask price

        if quantity is None:
            raise (ValueError("No quantity specified in call to submit_buy_order"))

        quantity = int(quantity)

        if quantity <= 0:
            raise (
                ValueError(
                    "Quantity must be positive number in call to submit_buy_order"
                )
            )

        payload = {}

        for field, value in [
            ("account", self.get_account()["url"]),
            ("instrument", instrument_URL),
            ("symbol", symbol),
            ("type", order_type),
            ("time_in_force", time_in_force),
            ("trigger", trigger),
            ("price", price),
            ("stop_price", stop_price),
            ("quantity", quantity),
            ("side", side),
        ]:
            if value is not None:
                payload[field] = value

        res = self.post(urls.build_orders(), data=payload)
        return res

    def place_order(
        self,
        instrument,
        quantity=1,
        price=0.0,
        transaction=None,
        trigger="immediate",
        order="market",
        time_in_force="gfd",
    ):
        """Place an order with Robinhood

        Args:
            instrument (dict): the RH URL and symbol in dict for the instrument to
                be traded
            quantity (int): quantity of stocks in order
            bid_price (float): price for order
            transaction (:obj:`Transaction`): BUY or SELL enum
            trigger (:obj:`Trigger`): IMMEDIATE or STOP enum
            order (:obj:`Order`): MARKET or LIMIT
            time_in_force (:obj:`TIME_IN_FORCE`): GFD or GTC (day or until
                cancelled)

        Returns:
            (:obj:`requests.request`): result from `orders` put command

        """

        if isinstance(transaction, str):
            transaction = Transaction(transaction)

        if not price:
            price = self.quote_data(instrument["symbol"])["bid_price"]

            if (price == 0) or (price is None):
                price = self.quote_data(instrument["symbol"])["last_trade_price"]

        payload = {
            "account": self.get_account()["url"],
            "instrument": unquote(instrument["url"]),
            "symbol": instrument["symbol"],
            "type": order.lower(),
            "time_in_force": time_in_force.lower(),
            "trigger": trigger,
            "quantity": quantity,
            "side": transaction.name.lower(),
        }

        if order.lower() == "stop":
            payload["stop_price"] = float(price)
        else:
            payload["price"] = float(price)

        res = self.post(urls.build_orders(), data=payload)
        return res

    def place_buy_order(self, instrument, quantity, ask_price=0.0):
        """Wrapper for placing buy orders

        Args:
            instrument (dict): the RH URL and symbol in dict for the instrument to
                be traded
            quantity (int): quantity of stocks in order
            ask_price (float): price for order (OPTIONAL! If not given, ask_price is
                automatic.)

        Returns:
            (:obj:`requests.request`): result from `orders` put command

        """

        if not ask_price:
            ask_price = self.quote_data(instrument["symbol"])["ask_price"]

            if (ask_price == 0) or (ask_price is None):
                ask_price = self.quote_data(instrument["symbol"])["last_trade_price"]

        transaction = Transaction.BUY

        return self.place_order(instrument, quantity, ask_price, transaction)

    def place_sell_order(self, instrument, quantity, bid_price=0.0):
        """Wrapper for placing sell orders

        Args:
            instrument (dict): the RH URL and symbol in dict for the instrument to
                be traded
            quantity (int): quantity of stocks in order
            bid_price (float): price for order (OPTIONAL! If not given, bid_price is
                automatic.)

        Returns:
            (:obj:`requests.request`): result from `orders` put command

        """
        if not bid_price:
            bid_price = self.quote_data(instrument["symbol"])["bid_price"]

            if (bid_price == 0) or (bid_price is None):
                bid_price = self.quote_data(instrument["symbol"])["last_trade_price"]

        transaction = Transaction.SELL

        return self.place_order(instrument, quantity, bid_price, transaction)

    ##############################
    # GET OPEN ORDER(S)
    ##############################

    def get_open_orders(self):
        """Returns all currently open (cancellable) orders.

        If not orders are currently open, `None` is returned.

        TODO: Is there a way to get these from the API endpoint without stepping through
            order history?
        """

        open_orders = []
        orders = self.order_history()
        for order in orders["results"]:
            if order["cancel"] is not None:
                open_orders.append(order)

        return open_orders

    ##############################
    #        CANCEL ORDER        #
    ##############################

    # TODO: Fix function complexity
    def cancel_order(self, order_id):  # noqa: C901
        """Cancels specified order and returns the response.

        If order cannot be cancelled, `None` is returned.
        (results from `orders` command).

        Args:
            order_id (str or dict): Order ID string that is to be cancelled or open
                order dict returned from order get.

        Returns:
            (:obj:`requests.request`): result from `orders` put command

        """
        if isinstance(order_id, str):
            try:
                order = self.get(urls.build_orders(order_id))
            except (requests.exceptions.HTTPError) as err_msg:
                raise ValueError(
                    "Failed to get Order for ID: "
                    + order_id
                    + "\n Error message: "
                    + repr(err_msg)
                )

            if order.get("cancel") is not None:
                try:
                    res = self.post(order["cancel"])
                    return res
                except requests.exceptions.HTTPError:
                    try:
                        # sometimes Robinhood asks for another log in when placing an
                        # order
                        res = self.post(order["cancel"])
                        return res
                    except (requests.exceptions.HTTPError) as err_msg:
                        raise ValueError(
                            "Failed to cancel order ID: "
                            + order_id
                            + "\n Error message: "
                            + repr(err_msg)
                        )
                        return None

        elif isinstance(order_id, dict):
            order_id = order_id["id"]
            try:
                order = self.get(urls.build_orders(order_id))
            except (requests.exceptions.HTTPError) as err_msg:
                raise ValueError(
                    "Failed to get Order for ID: "
                    + order_id
                    + "\n Error message: "
                    + repr(err_msg)
                )

            if order.get("cancel") is not None:
                try:
                    res = self.post(order["cancel"])
                    return res
                except requests.exceptions.HTTPError:
                    try:
                        # sometimes Robinhood asks for another log in when placing an
                        # order
                        res = self.post(order["cancel"])
                        return res
                    except requests.exceptions.HTTPError as err_msg:
                        raise ValueError(
                            "Failed to cancel order ID: "
                            + order_id
                            + "\n Error message: "
                            + repr(err_msg)
                        )
                        return None

        elif not isinstance(order_id, str) or not isinstance(order_id, dict):
            raise ValueError(
                "Cancelling orders requires a valid order_id string or open order"
                "dictionary"
            )

        # Order type cannot be cancelled without a valid cancel link
        else:
            raise ValueError("Unable to cancel order ID: " + order_id)


class RobinhoodSchema(SessionManagerSchema):
    """Schema for the Robinhood class."""

    __model__ = Robinhood
