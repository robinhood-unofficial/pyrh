"""Option Chain data class."""

from typing import Any, Iterable

from marshmallow import fields

from pyrh import urls

from .base import BaseModel, BaseSchema, base_paginator
from .option import MinTicksSchema, Option, OptionPaginatorSchema


class Chain(BaseModel):
    """Chain data class. Represents an option chain."""

    def get_chain(self, **kwargs: Any) -> Iterable[Option]:
        """Get a generator of options consisting of the option chain.

        Args:
            **kwargs: If the query argument is provided, the returned values will
                be restricted to option instruments that match the query. Possible
                query parameters: state (active), tradability, type (call vs put),
                 expiration_dates, strike_price, chain_id

        Returns:
            A generator of Options.
        """
        query = {"chain_id": str(self.id), "chain_symbol": self.symbol}
        valid_params = frozenset(
            [
                "chain_symbol",
                "state",
                "tradability",
                "type",
                "expiration_dates",
                "strike_price",
                "chain_id",
            ]
        )
        query.update({k: v for k, v in kwargs.items() if k in valid_params})
        # TODO should we allow chain_symbol, chain_id to be overwritten?
        url = urls.OPTIONS_INSTRUMENTS_BASE.with_query(**query)
        return base_paginator(url, self, OptionPaginatorSchema())


class ChainSchema(BaseSchema):
    """Chain schema data loader."""

    __model__ = Chain

    id = fields.UUID()
    symbol = fields.Str()
    can_open_position = fields.Bool()
    cash_component = fields.Float(allow_none=True)
    expiration_dates = fields.List(fields.Str())
    trade_value_multiplier = fields.Float()
    underlying_instruments = fields.List(fields.Dict())
    min_ticks = fields.Nested(MinTicksSchema)
