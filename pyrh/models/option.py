"""Option data class."""

from marshmallow import fields

from .base import BaseModel, BaseSchema


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

    chain_id = fields.String()
    chain_symbol = fields.String()
    created_at = fields.DateTime()
    expiration_date = fields.Date()
    id = fields.String()
    issue_date = fields.Date()
    min_ticks = fields.Nested(MinTicksSchema)
    rhs_tradability = fields.String()
    state = fields.String()
    strike_price = fields.Float()
    tradability = fields.String()
    type = fields.String()
    updated_at = fields.DateTime()
    url = fields.URL()
