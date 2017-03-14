from os import path
from datetime import datetime

import pytest

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

    def test_validate_quote(self, config=CONFIG):
        """validate fetcher"""
        rh_obj = Robinhood()
        data = rh_obj.quote_data(self.test_ticker)
        if data['updated_at'] == TEST_QUOTE['updated_at']:
            assert data == TEST_QUOTE
        else:
            for key in data.keys(): #SKIP PRICE DATA
                if key in TESTABLE_KEYS:
                    assert data[key] == TEST_QUOTE[key]

    def test_validate_fail_quote(self, config=CONFIG):
        """validate bad-path exception"""
        rh_obj = Robinhood()
        with pytest.raises(NameError):
            data = rh_obj.quote_data(self.fake_ticker)

    def test_validate_get_quote(self, config=CONFIG):
        """validate `get_quote` call"""
        pass

    def test_validate_ask_price(self, config=CONFIG):
        """validate `ask_price` call"""
        pass

    def test_ask_size(self, config=CONFIG):
        """validate `ask_size` call"""
        pass


