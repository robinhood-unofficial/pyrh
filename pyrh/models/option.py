"""Option data class."""
from typing import Any, Iterable, cast

from marshmallow import fields
from yarl import URL

from pyrh import exceptions, urls

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

    def __repr__(self) -> str:
        """Return the object as a string.

        Returns:
            The string representation of the object.

        """
        return (
            f"Option<{self.chain_symbol}|{self.strike_price}|"
            + f"{self.type}|{self.expiration_date}>"
        )


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


class OptionPosition(BaseModel):
    """Robinhood Option position data class. Represents an option position."""

    def __repr__(self) -> str:
        """Return the object as a string.

        Returns:
            The string representation of the object.

        """
        underlying = getattr(self, "underlying", self.option)
        return f"OptionPosition<{underlying}|{self.quantity}|{self.type}>"


class OptionPositionSchema(BaseSchema):
    """Robinhood Option position schema data loader."""

    __model__ = OptionPosition

    account = (fields.URL(),)
    average_price = (fields.Float(),)
    chain_id = (fields.UUID(),)
    chain_symbol = (fields.String(),)
    id = (fields.UUID(),)
    option = (fields.URL(),)
    type = (fields.String(),)  # should this be an enum?
    pending_buy_quantity = (fields.Float(),)
    pending_expired_quantity = (fields.Float(),)
    pending_expiration_quantity = (fields.Float(),)
    pending_exercise_quantity = (fields.Float(),)
    pending_assignment_quantity = (fields.Float(),)
    pending_sell_quantity = (fields.Float(),)
    quantity = (fields.Float(),)
    intraday_quantity = (fields.Float(),)
    intraday_average_open_price = (fields.Float(),)
    created_at = (fields.DateTime(),)
    trade_value_multiplier = (fields.Float(),)
    updated_at = (fields.DateTime(),)
    url = (fields.URL(),)


class OptionQuote(BaseModel):
    """Robinhood Option quote data class. Represents an option quote."""

    def __repr__(self) -> str:
        """Return the object as a string.

        Returns:
            The string representation of the object.

        """
        return f"""OptionQuote<
        Ask: {self.ask_size} x {self.ask_price}
        Bid: {self.bid_size} x {self.bid_price}
        Low: {self.low_price} | High: {self.high_price}
        Volume: {self.volume} | Open Interest: {self.open_interest}
        Implied Volatility: {self.implied_volatility}
        Delta: {self.delta} | Gamma: {self.gamma} | Rho: {self.rho}
        Theta: {self.theta} | Vega: {self.vega}
        >"""


class OptionQuoteSchema(BaseSchema):
    """Robinhood Option quote schema data loader."""

    __model__ = OptionQuote

    adjusted_mark_price = (fields.Float(),)
    ask_price = (fields.Float(),)
    ask_size = (fields.Integer(),)
    bid_price = (fields.Float(),)
    bid_size = (fields.Integer(),)
    break_even_price = (fields.Float(),)
    high_price = (fields.Float(),)
    instrument = (fields.URL(),)
    last_trade_price = (fields.Float(),)
    last_trade_size = (fields.Integer(),)
    low_price = (fields.Float(),)
    mark_price = (fields.Float(),)
    open_interest = (fields.Integer(),)
    previous_close_date = (fields.Date(),)
    previous_close_price = (fields.Float(),)
    volume = (fields.Integer(),)
    chance_of_profit_long = (fields.Float(),)
    chance_of_profit_short = (fields.Float(),)
    delta = (fields.Float(),)
    gamma = (fields.Float(),)
    implied_volatility = (fields.Float(),)
    rho = (fields.Float(),)
    theta = (fields.Float(),)
    vega = (fields.Float(),)
    high_fill_rate_buy_price = (fields.Float(),)
    high_fill_rate_sell_price = (fields.Float(),)
    low_fill_rate_buy_price = (fields.Float(),)
    low_fill_rate_sell_price = (fields.Float(),)


class OptionPositionPaginator(BasePaginator):
    """Thin wrapper around `self.results`, a list of `Option` objs."""

    pass


class OptionPositionPaginatorSchema(BasePaginatorSchema):
    """Schema class for the OptionPaginator.

    The nested results are of type `OptionPosition`.

    """

    __model__ = OptionPositionPaginator

    results = fields.List(fields.Nested(OptionPositionSchema))


class OptionManager(SessionManager):
    """Group together methods that manipulate an options."""

    def _get_option_from_url(self, option_url: URL) -> Option:
        """Get option from option_url.

        Args:
            option_url: url to the option, used for getting the underlying option
                for an options position.

        Returns:
            An Option object.
        """
        option_data = self.get(option_url)
        return cast(Option, OptionSchema().load(option_data))

    def _get_option_quote(self, option_id: str) -> OptionQuote:
        """Get quote from option id.

        Args:
            option_id: underlying option id to get quote for

        Returns:
            An OptionQuote object.
        """
        quote_data = self.get_url(
            urls.MARKET_DATA_BASE.join(URL(f"options/{option_id}/"))
        )
        return cast(OptionQuote, OptionQuoteSchema().load(quote_data))

    def _get_option_positions(self, open_pos: bool = True) -> Iterable[OptionPosition]:
        # TODO figure out what /?nonzero=true is, returns quantity = 0...
        url = urls.OPTIONS_BASE.join(URL("positions/?nonzero=true"))
        positions = base_paginator(url, self, OptionPositionPaginatorSchema())
        if open_pos:
            positions = [p for p in positions if float(p.quantity) > 0]
        for p in positions:
            p.underlying = self._get_option_from_url(p.option)
        return positions

    def _get_option_id(
        self, symbol: str, strike: str, expiry: str, otype: str, state: str = "active"
    ) -> str:
        url = urls.OPTIONS_BASE.join(URL("instruments/"))
        params = {
            "chain_symbol": symbol,
            "strike_price": strike,
            "expiration_dates": expiry,
            "type": otype,
            "state": state,
        }
        results = self.get_url(url.with_query(**params)).get("results")
        if not results:
            e = """
            Couldn't find option with symbol={}, strike={}, expiry={}, type={}, state={}
            """.format(
                symbol, strike, expiry, otype, state
            )
            raise exceptions.InvalidOptionId(e)
        return str(results[0]["id"])

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
