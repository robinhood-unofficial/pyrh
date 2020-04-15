import datetime as dt
import numbers
from os import path

import requests
from dateutil import parser as p
from six import string_types

from pyrh.models.option import MinTicks, OptionSchema



HERE = path.abspath(path.dirname(__file__))
ROOT = path.dirname(HERE)

# Setup
sample_url = "https://api.robinhood.com/options/instruments/f098f169-74f9-4b91-b955-6834e1b67a12/"
response = requests.get(sample_url)
data = response.json()
option_schema = OptionSchema()
option_obj = option_schema.load(data)


def test_chain_symbol():
    symbol = option_obj.chain_symbol
    assert isinstance(symbol, string_types)
    assert symbol == "AAPL"


def test_strike_price():
    strike = option_obj.strike_price
    assert isinstance(strike, numbers.Real)
    assert strike == 232.5


def test_expiration_date():
    expiry = option_obj.expiration_date
    assert isinstance(expiry, dt.date)
    assert expiry == dt.date(2020, 4, 17)


def test_created_at():
    created_at = option_obj.created_at
    assert isinstance(created_at, dt.datetime)
    assert created_at == p.parse("2020-03-31T01:27:43.249339Z")


def test_min_ticks():
    min_ticks = option_obj.min_ticks
    assert isinstance(min_ticks, MinTicks)
    assert min_ticks.above_tick == 0.05
    assert min_ticks.below_tick == 0.01
    assert min_ticks.cutoff_price == 3.00
