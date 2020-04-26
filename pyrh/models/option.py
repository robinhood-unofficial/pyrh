"""Option data class."""
from typing import Any, Iterable

from marshmallow import fields

from pyrh import urls

from .base import (
    BaseModel,
    BasePaginator,
    BasePaginatorSchema,
    BaseSchema,
    base_paginator,
)
from .sessionmanager import SessionManager


class MinTicks(BaseModel):
    """Min ticks data class. Describes min increments the option can be traded at."""

    pass


class MinTicksSchema(BaseSchema):
    """Min ticks schema data loader."""

    __model__ = MinTicks

    above_tick = fields.Float()
    below_tick = fields.Float()
    cutoff_price = fields.Float()


class Option(BaseModel):
    """Robinhood Option data class. Represents an options instrument."""

    pass


class OptionSchema(BaseSchema):
    """Robinhood Option schema data loader."""

    __model__ = Option

    chain_id = fields.UUID()
    chain_symbol = fields.String()
    created_at = fields.DateTime()
    expiration_date = fields.Date()
    id = fields.UUID()
    issue_date = fields.Date()
    min_ticks = fields.Nested(MinTicksSchema)
    rhs_tradability = fields.String()
    state = fields.String()
    strike_price = fields.Float()
    tradability = fields.String()
    type = fields.String()
    updated_at = fields.DateTime()
    url = fields.URL()


class OptionPaginator(BasePaginator):
    """Thin wrapper around `self.results`, a list of `Option` objs."""

    pass


class OptionPaginatorSchema(BasePaginatorSchema):
    """Schema class for the OptionPaginator.

    The nested results are of type `Option`.

    """

    __model__ = OptionPaginator

    results = fields.List(fields.Nested(OptionSchema))


class OptionManager(SessionManager):
    """Group together methods that manipulate an options."""

    def get_options(self, **kwargs: Any) -> Iterable[Option]:
        """Get a generator of options.

        Args:
            **kwargs: If the query argument is provided, the returned values will
                be restricted to option instruments that match the query. Possible
                query parameters: chain_symbol, chain_id, state (active),
                tradability, type (call vs put), expiration_dates, strike_price

        Returns:
            A generator of Options.
        """
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
        query = {k: v for k, v in kwargs.items() if k in valid_params}
        url = urls.OPTIONS_INSTRUMENTS_BASE.with_query(**query)
        return base_paginator(url, self, OptionPaginatorSchema())
