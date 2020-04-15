"""Option data class."""

from typing import Any

from marshmallow import fields, post_load

from pyrh.common import JSON

from .base import BaseModel, BaseSchema


class Option(BaseModel):
    """Robinhood Option data class. Represents an options instrument."""

    pass


class OptionSchema(BaseSchema):
    """Robinhood Option schema data loader."""

    __model__ = Option

    chain_id = fields.String()
    chain_symbol = fields.String()
    created_at = fields.NaiveDateTime()
    expiration_date = fields.Date()
    id = fields.String()
    issue_date = fields.Date()
    min_ticks = fields.Dict()
    rhs_tradability = fields.String()
    state = fields.String()
    strike_price = fields.Float()
    tradability = fields.String()
    type = fields.String()
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
        data = data.get("results", [{}])[0]
        return self.__model__(**data)
