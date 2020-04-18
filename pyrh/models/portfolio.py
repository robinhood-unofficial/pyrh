"""Current portfolio."""

from marshmallow import fields

from .base import BaseModel, BaseSchema


class Portfolio(BaseModel):
    """Robinhood portfolio data class."""

    pass


class PortfolioSchema(BaseSchema):
    """Robinhood portfolio schema data loader."""

    __model__ = Portfolio
    __first__ = "results"  # returns a paginator but we only need the first

    url = fields.URL()
    account = fields.URL()
    start_date = fields.NaiveDateTime()
    market_value = fields.Float()
    equity = fields.Float()
    extended_hours_market_value = fields.Float()
    extended_hours_equity = fields.Float()
    extended_hours_portfolio_equity = fields.Float()
    last_core_market_value = fields.Float()
    last_core_equity = fields.Float()
    last_core_portfolio_equity = fields.Float()
    excess_margin = fields.Float()
    excess_maintenance = fields.Float()
    excess_margin_with_uncleared_deposits = fields.Float()
    portfolio_equity_previous_close = fields.Float()
    adjusted_equity_previous_close = fields.Float()
    adjusted_portfolio_equity_previous_close = fields.Float()
    withdrawable_amount = fields.Float()
    unwithdrawable_deposits = fields.Float()
    unwithdrawable_grants = fields.Float()
