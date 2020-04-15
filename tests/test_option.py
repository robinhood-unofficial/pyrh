import datetime as dt
import numbers
from os import path

import pytest
import requests
from six import string_types

from pyrh.models.option import OptionSchema


HERE = path.abspath(path.dirname(__file__))
ROOT = path.dirname(HERE)

# Setup
sample_url = "https://api.robinhood.com/options/instruments/f098f169-74f9-4b91-b955-6834e1b67a12/"
response = requests.get(sample_url)
data = response.json()
option_schema = OptionSchema()
option_obj = option_schema.make_object(data=data)


def test_chain_symbol():
    symbol = option_obj.chain_symbol
    assert isinstance(string_types, symbol)
    assert symbol == "AAPL"


def test_strike_price():
    strike = option_obj.strike
    assert isinstance(numbers.Real, strike)
    assert format(strike, ".4f") == 232.5000


def test_expiration_date():
    expiry = option_obj.expiration_date
    assert isinstance(dt.datetime.date, expiry)
    assert expiry == dt.date(2020, 4, 17)


def test_created_at():
    created_at = option_obj.created_at
    assert isinstance(dt.datetime, created_at)
    assert created_at == dt.datetime.strptime(created_at, "%Y-%m-%dT%H:%M:%S.%fZ")


def test_min_ticks():
    min_ticks = option_obj.min_ticks
    assert isinstance(dict(), min_ticks)
    assert min_ticks == {
        "above_tick": "0.05",
        "below_tick": "0.01",
        "cutoff_price": "3.00",
    }
