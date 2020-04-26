"""Option Chain data class."""

from marshmallow import fields

from .base import BaseModel, BaseSchema
from .option import MinTicksSchema


class Chain(BaseModel):
    """Chain data class. Represents an option chain."""

    pass


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
