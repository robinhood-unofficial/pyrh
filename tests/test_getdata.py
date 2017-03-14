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
def test_quote_endpoint(config=CONFIG):
    """get raw data from Robinhood to test against"""
    global TEST_QUOTE

    try:
        data = helpers.fetch_REST_directly(
            'quotes',
            config.get('FETCH', 'test_ticker'),
            config
        )
    except Exception:
        global STOP_TEST
        STOP_TEST = True
        raise

    TEST_QUOTE = data



