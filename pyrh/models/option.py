"""Option data class."""

from marshmallow import fields

from .base import BaseModel, BasePaginator, BasePaginatorSchema, BaseSchema


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
