"""Define Robinhood endpoints."""

from yarl import URL


# Base
API_BASE = URL("https://api.robinhood.com")

# General
ACCOUNTS = API_BASE.with_path("/accounts/")
ACH_BASE = API_BASE.with_path("/ach/")  # not implemented
APPLICATIONS = API_BASE.with_path("/applications/")  # not implemented
DIVIDENDS = API_BASE.with_path("/dividends/")
DOCUMENTS = API_BASE.with_path("/documents/")  # not implemented
INSTRUMENTS_BASE = API_BASE.with_path("/instruments/")
MARGIN_UPGRADES = API_BASE.with_path("/margin/upgrades/")  # not implemented
MARKETS = API_BASE.with_path("/markets/")  # not implemented
NOTIFICATIONS = API_BASE.with_path("/notifications/")  # not implemented
DOCUMENT_REQUESTS = API_BASE.with_path("/upload/document_requests/")  # not implemented
PORTFOLIOS = API_BASE.with_path("/portfolios/")
POSITIONS = API_BASE.with_path("/positions/")
WATCHLISTS = API_BASE.with_path("/watchlists/")  # not implemented

# User
USER = API_BASE.with_path("/user/")
INVESTMENT_PROFILE = USER.with_path("/investment_profile/")

# Quotes
QUOTES = API_BASE.with_path("/quotes/")
HISTORICALS = QUOTES.with_path("/historicals/")

# Auth
OAUTH_BASE: URL = API_BASE.with_path("/oauth2/")
OAUTH: URL = OAUTH_BASE.with_path("/token/")
OAUTH_REVOKE: URL = OAUTH_BASE.with_path("/revoke_token/")
MIGRATE_TOKEN: URL = OAUTH_BASE.with_path("/migrate_token/")  # not implemented
PASSWORD_RESET: URL = API_BASE.with_path("/password_reset/request/")  # not implemented


def build_challenge(challenge_id: str) -> URL:
    """Build challenge response url.

    Args:
        challenge_id: the id of the challenge passed in the oauth request flow.

    Returns:
        The constructed URL with the challenge_id embedded in teh url path.

    """
    return API_BASE.with_path(f"/challenge/{challenge_id}/respond/")


def build_ach(option):
    """
    Combination of 3 ACH endpoints. Options include:
        * iav
        * relationships
        * transfers
    """
    return (
        ACH_BASE.with_path("/iav/auth/")
        if option == "iav"
        else ACH_BASE.with_path(f"/{option}/")
    )


def instruments(instrument_id=None, option=None):
    """
    Return information about a specific instrument by providing its instrument id.
    Add extra options for additional information such as "popularity"
    """
    url = INSTRUMENTS_BASE
    if instrument_id is not None:
        url.with_path(f"{instrument_id}")
        url += f"{instrument_id}"
    if option is not None:
        url += f"{option}"

    return url


def orders(order_id=""):
    return API_BASE.with_path(f"/orders/{order_id}/")


def news(stock):
    return API_BASE.with_path(f"/midlands/news/{stock}/")


def fundamentals(stock):
    return API_BASE.with_path(f"/fundamentals/{stock}/")


def tags(tag):
    """
    Returns endpoint with tag concatenated.
    """
    return API_BASE.with_path(f"/midlands/tags/tag/{tag}/")


def chain(instrument_id):
    return API_BASE.with_path(
        f"/options/chains/?equity_instrument_ids={instrument_id}/"
    )


def options(chain_id, dates, option_type):
    return API_BASE.with_path(
        f"/options/instruments/?chain_id={chain_id}&expiration_dates={dates}"
        f"&state=active&tradability=tradable&type={option_type}"
    )


def market_data(option_id):
    return API_BASE.with_path(f"/marketdata/options/{option_id}/")
