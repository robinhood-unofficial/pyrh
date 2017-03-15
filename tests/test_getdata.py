from os import path
from datetime import datetime

import pytest
from flaky import flaky

from Robinhood import Robinhood
import helpers

HERE = path.abspath(path.dirname(__file__))
ROOT = path.dirname(HERE)

CONFIG_FILENAME = path.join(HERE, 'test_config.cfg')

CONFIG = helpers.get_config(CONFIG_FILENAME)

STOP_TEST = False

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

        try:
            data = helpers.fetch_REST_directly(
                'quotes',
                self.test_ticker,
                config
            )
        except Exception:
            global STOP_TEST
            STOP_TEST = True
            raise

        TEST_QUOTE = data

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
