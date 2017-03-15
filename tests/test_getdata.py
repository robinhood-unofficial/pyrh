from os import path
from datetime import datetime

import pytest
from flaky import flaky
import requests

from Robinhood import Robinhood
import helpers

HERE = path.abspath(path.dirname(__file__))
ROOT = path.dirname(HERE)

CONFIG_FILENAME = path.join(HERE, 'test_config.cfg')

CONFIG = helpers.get_config(CONFIG_FILENAME)

TEST_QUOTE = {}

TESTABLE_KEYS = [
    'previous_close_date',
    'symbol',
    'trading_halted',
    'previous_close',
    'last_trade_price_source',
    'instrument'
]
@pytest.mark.incremental
class TestQuoteHelpers:
    """wrapper to test quote architecture in order"""
    test_ticker = CONFIG.get('FETCH', 'test_ticker')
    fake_ticker = CONFIG.get('FETCH', 'fake_ticker')
    rh_obj = Robinhood()
    def test_quote_endpoint(self, config=CONFIG):
        """get raw data from Robinhood to test against"""
        global TEST_QUOTE

        TEST_QUOTE = helpers.fetch_REST_directly(
            'quotes',
            self.test_ticker,
            config
        )

    def test_validate_quote(self):
        """validate fetcher"""
        data = self.rh_obj.quote_data(self.test_ticker)
        if data['updated_at'] == TEST_QUOTE['updated_at']:
            assert data == TEST_QUOTE
        else:
            for key in data.keys(): #SKIP PRICE DATA
                if key in TESTABLE_KEYS:
                    assert data[key] == TEST_QUOTE[key]

    def test_validate_fail_quote(self):
        """validate bad-path exception"""
        with pytest.raises(NameError):
            data = self.rh_obj.quote_data(self.fake_ticker)

    def test_validate_get_quote(self):
        """validate `get_quote` call"""
        data = self.rh_obj.get_quote(self.test_ticker)
        assert data == TEST_QUOTE['symbol']

    @flaky
    def test_validate_ask_price(self):
        """validate `ask_price` call"""
        data = self.rh_obj.ask_price(self.test_ticker)
        quote = self.rh_obj.quote_data(self.test_ticker)

        assert data == quote['ask_price']

    @flaky
    def test_validate_ask_size(self):
        """validate `ask_size` call"""
        data = self.rh_obj.ask_size(self.test_ticker)
        quote = self.rh_obj.quote_data(self.test_ticker)

        assert data == quote['ask_size']

    @flaky
    def test_validate_bid_price(self):
        """validate `bid_price` call"""
        data = self.rh_obj.bid_price(self.test_ticker)
        quote = self.rh_obj.quote_data(self.test_ticker)

        assert data == quote['bid_price']

    @flaky
    def test_validate_bid_size(self):
        """validate `bid_size` call"""
        data = self.rh_obj.bid_size(self.test_ticker)
        quote = self.rh_obj.quote_data(self.test_ticker)

        assert data == quote['bid_size']

    @flaky
    def test_validate_last_trade_price(self):
        """validate `last_trade_price` call"""
        data = self.rh_obj.last_trade_price(self.test_ticker)
        quote = self.rh_obj.quote_data(self.test_ticker)

        assert data == quote['last_trade_price']

    def test_validate_previous_close(self):
        """validate `previous_close` call"""
        data = self.rh_obj.previous_close(self.test_ticker)

        assert data == TEST_QUOTE['previous_close']

    def test_validate_previous_close_date(self):
        """validate `previous_close_date` call"""
        data = self.rh_obj.previous_close_date(self.test_ticker)

        assert data == TEST_QUOTE['previous_close_date']

    def test_validate_adjusted_previous_close(self):
        """validate `adjusted_previous_close` call"""
        data = self.rh_obj.adjusted_previous_close(self.test_ticker)

        assert data == TEST_QUOTE['adjusted_previous_close']

    def test_validate_symbol(self):
        """validate `symbol` call"""
        data = self.rh_obj.symbol(self.test_ticker)

        assert data == TEST_QUOTE['symbol']

    @flaky
    def test_validate_last_updated_at(self):
        """validate `last_updated_at` call"""
        data = self.rh_obj.last_updated_at(self.test_ticker)
        quote = self.rh_obj.quote_data(self.test_ticker)

        assert data == quote['updated_at']

TEST_FUNDAMENTAL = {}
@pytest.mark.incremental
class TestFundamentalsHelpers:
    """wrapper to test fundamental architecture in order"""
    test_ticker = CONFIG.get('FETCH', 'test_ticker')
    fake_ticker = CONFIG.get('FETCH', 'fake_ticker')
    rh_obj = Robinhood()
    def test_fundamental_endpoint(self, config=CONFIG):
        """get raw data from Robinhood to test against"""
        global TEST_FUNDAMENTAL

        TEST_FUNDAMENTAL = helpers.fetch_REST_directly(
            'fundamentals',
            self.test_ticker,
            config
        )

    def test_validate_fundamental(self):
        """validate fetcher"""
        data = self.rh_obj.get_fundamentals(self.test_ticker)
        assert data == TEST_FUNDAMENTAL

    def test_validate_fail_fundamental(self):
        """validate bad-path exception"""
        with pytest.raises(NameError):
            data = self.rh_obj.get_fundamentals(self.fake_ticker)

    def test_validate_fundamental_wrapper(self):
        main_data = self.rh_obj.fundamentals(self.test_ticker)
        wrapped_data = self.rh_obj.fundamentals(self.test_ticker)

        assert wrapped_data == main_data
        assert wrapped_data == TEST_FUNDAMENTAL

TEST_URL_RESULT = {}
@pytest.mark.incremental
class TestURLWrapper:
    """make sure get_url returns expected behavior"""
    base_url = 'https://api.robinhood.com/'
    rh_obj = Robinhood()
    def test_url_endpoint(self):
        """fetch url directly"""
        global TEST_URL_RESULT

        req = requests.get(self.base_url)
        req.raise_for_status()

        TEST_URL_RESULT = req.json()

    def test_get_url(self):
        """fetch url with get_url"""
        data = self.rh_obj.get_url(self.base_url)
        assert data == TEST_URL_RESULT

