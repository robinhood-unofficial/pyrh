import datetime as dt
import numbers
from os import path

import requests
from six import string_types

from pyrh.models.chain import Chain, ChainSchema
from pyrh.models.option import MinTicks


HERE = path.abspath(path.dirname(__file__))
ROOT = path.dirname(HERE)

# Setup
sample_url = (
    "https://api.robinhood.com/options/chains/cee01a93-626e-4ee6-9b04-60e2fd1392d1/"
)
response = requests.get(sample_url)
data = response.json()
chain_schema = ChainSchema()
chain_obj = chain_schema.load(data)


def test_chain_symbol():
    symbol = chain_obj.symbol
    assert isinstance(symbol, string_types)
    assert symbol == "AAPL"


def test_min_ticks():
    min_ticks = chain_obj.min_ticks
    assert isinstance(min_ticks, MinTicks)
    assert min_ticks.above_tick == 0.05
    assert min_ticks.below_tick == 0.01
    assert min_ticks.cutoff_price == 3.00
