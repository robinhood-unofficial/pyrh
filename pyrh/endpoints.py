"""Define Robinhood endpoints."""

from typing import Callable

from yarl import URL


BASE = URL("https://api.robinhood.com")

# OAuth
OAUTH: URL = BASE.with_path("/oauth2/token/")
OAUTH_REVOKE: URL = BASE.with_path("/oauth2/revoke_token/")
CHALLENGE: Callable[[str], URL] = lambda cid: BASE.with_path(
    f"/challenge/{cid}/respond"
)


def logout():
    return BASE.with_path("/oauth2/revoke_token/")


def investment_profile():
    return BASE.with_path("/user/investment_profile/")


def accounts():
    return BASE.with_path("/accounts/")


def ach(option):
    """
    Combination of 3 ACH endpoints. Options include:
        * iav
        * relationships
        * transfers
    """
    return (
        BASE.with_path("/ach/iav/auth/")
        if option == "iav"
        else BASE.with_path(f"/ach/{option}/")
    )


def applications():
    return BASE.with_path("/applications/")


def dividends():
    return BASE.with_path("/dividends/")


def edocuments():
    return BASE.with_path("/documents/")


def instruments(instrument_id=None, option=None):
    """
    Return information about a specific instrument by providing its instrument id.
    Add extra options for additional information such as "popularity"
    """
    url = BASE.with_path(f"/instruments/")
    if instrument_id is not None:
        url += f"{instrument_id}"
    if option is not None:
        url += f"{option}"

    return url


def margin_upgrades():
    return BASE.with_path("/margin/upgrades/")


def markets():
    return BASE.with_path("/markets/")


def notifications():
    return BASE.with_path("/notifications/")


def orders(order_id=""):
    return BASE.with_path(f"/orders/{order_id}/")


def password_reset():
    return BASE.with_path("/password_reset/request/")


def portfolios():
    return BASE.with_path("/portfolios/")


def positions():
    return BASE.with_path("/positions/")


def quotes():
    return BASE.with_path("/quotes/")


def historicals():
    return BASE.with_path("/quotes/historicals/")


def document_requests():
    return BASE.with_path("/upload/document_requests/")


def user():
    return BASE.with_path("/user/")


def watchlists():
    return BASE.with_path("/watchlists/")


def news(stock):
    return BASE.with_path(f"/midlands/news/{stock}/")


def fundamentals(stock):
    return BASE.with_path(f"/fundamentals/{stock}/")


def tags(tag):
    """
    Returns endpoint with tag concatenated.
    """
    return BASE.with_path(f"/midlands/tags/tag/{tag}/")


def chain(instrument_id):
    return BASE.with_path(f"/options/chains/?equity_instrument_ids={instrument_id}/")


def options(chain_id, dates, option_type):
    return BASE.with_path(
        f"/options/instruments/?chain_id={chain_id}&expiration_dates={dates}"
        f"&state=active&tradability=tradable&type={option_type}"
    )


def market_data(option_id):
    return BASE.with_path(f"/marketdata/options/{option_id}/")


def convert_token():
    return BASE.with_path("/oauth2/migrate_token/")
