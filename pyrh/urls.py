"""Define Robinhood endpoints."""

from typing import Optional

from yarl import URL

# TODO: All url construction should happen here, not in robinhood.py

# Base
API_BASE = URL("https://api.robinhood.com")

# General
ACCOUNTS = API_BASE / "accounts/"
ACH_BASE = API_BASE / "ach/"  # not implemented
APPLICATIONS = API_BASE / "applications/"  # not implemented
DIVIDENDS = API_BASE / "dividends/"
DOCUMENTS = API_BASE / "documents/"  # not implemented
DOCUMENT_REQUESTS = API_BASE / "upload/document_requests/"  # not implemented
FUNDAMENTALS_BASE = API_BASE / "fundamentals/"
INSTRUMENTS_BASE = API_BASE / "instruments/"
MARGIN_UPGRADES = API_BASE / "margin/upgrades/"  # not implemented
MARKETS = API_BASE / "markets/"  # not implemented
MARKET_DATA_BASE = API_BASE / "marketdata/"
NEWS_BASE = API_BASE / "midlands/news/"
NOTIFICATIONS = API_BASE / "notifications/"  # not implemented
ORDERS_BASE = API_BASE / "orders/"
PORTFOLIOS = API_BASE / "portfolios/"
POSITIONS = API_BASE / "positions/"
TAGS_BASE = API_BASE / "midlands/tags/tag/"
WATCHLISTS = API_BASE / "watchlists/"

# Options
OPTIONS_BASE = API_BASE / "options/"
OPTIONS_CHAIN_BASE = OPTIONS_BASE / "chains/"
OPTIONS_INSTRUMENTS_BASE = OPTIONS_BASE / "instruments/"

# User
USER = API_BASE / "user/"
INVESTMENT_PROFILE = USER / "investment_profile/"

# Quotes
QUOTES = API_BASE / "quotes/"
HISTORICALS = QUOTES / "historicals/"

# Auth
OAUTH_BASE: URL = API_BASE / "oauth2/"
OAUTH: URL = OAUTH_BASE / "token/"
OAUTH_REVOKE: URL = OAUTH_BASE / "revoke_token/"
MIGRATE_TOKEN: URL = OAUTH_BASE / "migrate_token/"  # not implemented
PASSWORD_RESET: URL = API_BASE / "password_reset/request/"  # not implemented


def build_challenge(challenge_id: str) -> URL:
    """Build challenge response url.

    Args:
        challenge_id: the id of the challenge passed in the oauth request flow.

    Returns:
        The constructed URL with the challenge_id embedded in teh url path.

    """
    return API_BASE / f"challenge/{challenge_id}/respond/"


def build_ach(option: str) -> URL:
    """
    Combination of 3 ACH endpoints. Options include:
        * iav
        * relationships
        * transfers
    """
    return ACH_BASE / "iav/auth/" if option == "iav" else ACH_BASE / f"{option}/"


def instruments(
    symbol: Optional[str] = None, query: Optional[str] = None, id_: Optional[str] = None
) -> URL:
    """Construct urls that query instruments.

    Note:
        Each of the arguments are mutually exclusive.

    Args:
        symbol: A stock ticker symbol.
        query: Keyword to search for an instrument. (might be in name or ticker)
        id_: The UUID that represents the instrument.

    Returns:
        A constructed URL with the embedded query parameter

    """
    # Note:
    # INSTRUMENTS_BASE/{instrument_id}/splits will not be implemented since the url is
    # embedded in the results of an individual instrument result. The same logic applies
    # for INSTRUMENTS_BASE/{instrument_id}/splits/{split_id}/
    if symbol is not None:
        return INSTRUMENTS_BASE.with_query(symbol=symbol)
    elif query is not None:
        return INSTRUMENTS_BASE.with_query(query=query)
    elif id_ is not None:
        return INSTRUMENTS_BASE / f"{id_}/"


def build_orders(order_id: Optional[str] = None) -> URL:
    """Build endpoint to place orders."

    Args:
        order_id: the id of the order

    Returns:
        A constructed URL for a particular order or the base URL for all orders.

    """
    if order_id is not None:
        return ORDERS_BASE / f"{order_id}/"
    else:
        return ORDERS_BASE


def build_news(stock: str) -> URL:
    """Build news endpoint for a particular stock

    Args:
        stock: The stock ticker to build the URL

    Returns:
        A constructed URL for the input stock ticker.

    """
    return NEWS_BASE / f"{stock}/"


def build_fundamentals(stock: str) -> URL:
    """Build fundamentals endpoint for a particular stock

    Args:
        stock: The stock ticker to build the URL

    Returns:
        A constructed URL of the fundamentals for the input stock ticker.

    """
    return FUNDAMENTALS_BASE / f"{stock}/"


def build_tags(tag: str) -> URL:
    """Build endpoints for tickers with a particular tag.

    Args:
        tag: The tag to search for.

    Returns:
        A constructed URL for a particular tag.

    """
    return TAGS_BASE / f"{tag}/"


def build_chain(instrument_id: str) -> URL:
    """Build the query for a particular options chain.

    # TODO: this isn't best practice
    # (query construction should be a separate function)

    Args:
        instrument_id: The instrument in question.

    Returns:
        A constructed URL for the particular options chain search.

    """
    return (
        OPTIONS_CHAIN_BASE.with_query(equity_instrument_ids=f"{instrument_id}") / "/"
    )  # TODO: find out if this trailing slash is required.


def build_options(chain_id: str, dates: str, option_type: str) -> URL:
    """Build options search endpoint.

    # TODO: this really isn't best practice.

    Args:
        chain_id: The id for a particular options chain.
        dates: The range of dates to procure # TODO: document the format of the dates
        option_type: The type of the option # TODO: document the types
    """
    return OPTIONS_INSTRUMENTS_BASE.with_query(
        chain_id=f"{chain_id}",
        expiration_dates=f"{dates}",
        state="active",
        tradability="tradable",
        type=f"{option_type}",
    )


def build_market_data(option_id: Optional[str] = None) -> URL:
    """Build market data endpoint.

    Args:
        option_id: the id of the option.

    Returns:
        A constructed URL for market data for a particular `option_id`.
    """
    if option_id is None:
        return MARKET_DATA_BASE / f"{option_id}/"
    else:
        return MARKET_DATA_BASE
