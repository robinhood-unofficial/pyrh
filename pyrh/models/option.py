"""Current portfolio."""

from typing import Any

from marshmallow import fields, post_load

from pyrh.common import JSON

from .base import BaseModel, BaseSchema


class Option(BaseModel):
    """Robinhood Option data class. Represents an options instrument"""

    pass


class OptionSchema(BaseSchema):
    """Robinhood Option schema data loader.
    Sample result payload from 
    {
        "chain_id": "cee01a93-626e-4ee6-9b04-60e2fd1392d1",
        "chain_symbol": "AAPL",
        "created_at": "2020-03-31T01:27:43.249339Z",
        "expiration_date": "2020-04-17",
        "id": "f098f169-74f9-4b91-b955-6834e1b67a12",
        "issue_date": "2004-11-29",
        "min_ticks": {
            "above_tick": "0.05",
            "below_tick": "0.01",
            "cutoff_price": "3.00"
        },
        "rhs_tradability": "untradable",
        "state": "active",
        "strike_price": "232.5000",
        "tradability": "tradable",
        "type": "put",
        "updated_at": "2020-03-31T01:27:43.249354Z",
        "url": "https://api.robinhood.com/options/instruments/f098f169-74f9-4b91-b955-6834e1b67a12/"
    }
    """

    __model__ = Options

    chain_id = fields.String()
    chain_symbol = fields.String()
    created_at = fields.NaiveDateTime()
    expiration_date = fields.Date()
    options_id = fields.String() 
    issue_date = fields.Date()
    min_ticks = fields.Dict()
    rhs_tradability = fields.String()
    state = fields.String()
    strike_price = fields.Float()
    tradability = fields.String()
    options_type = fields.String()  
    updated_at = fields.NaiveDateTime()
    url = fields.URL()  

    @post_load
    def make_object(self, data: JSON, **kwargs: Any) -> Option:
        """Build model for the Option class.

        Args:
            data: The JSON diction to use to build the Option.
            **kwargs: Unused but required to match signature of `Schema.make_object`

        Returns:
            An instance of the Option class.

        """
        # Can potentially move this preprocessing part to a helper file
        prefix = self.__class__.__name__.lower()
        reserved_word_overwrite = ["type", "id"]
        for attr in reserved_word_overwrite:
            k, v = f"{prefix}_{attr}", data.pop("attr")
            data[k] = v

        data = data.get("results", [{}])[0]
        return self.__model__(**data)
