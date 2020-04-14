"""Define Robinhood endpoints."""

from .common import API_BASE


def investment_profile():
    return API_BASE.with_path("/user/investment_profile/")


def accounts():
    return API_BASE.with_path("/accounts/")


def ach(option):
    """
    Combination of 3 ACH endpoints. Options include:
        * iav
        * relationships
        * transfers
    """
    return (
        API_BASE.with_path("/ach/iav/auth/")
        if option == "iav"
        else API_BASE.with_path(f"/ach/{option}/")
    )


def applications():
    return API_BASE.with_path("/applications/")


def dividends():
    return API_BASE.with_path("/dividends/")


def edocuments():
    return API_BASE.with_path("/documents/")


def instruments(options=False):
    """
    Return information about a specific instrument by providing its instrument id.
    Add extra options for additional information such as "popularity"
    """
    opt = "/options" if options else ""
    return API_BASE.with_path(f"{opt}/instruments/")


def margin_upgrades():
    return API_BASE.with_path("/margin/upgrades/")


def markets():
    return API_BASE.with_path("/markets/")


def notifications():
    return API_BASE.with_path("/notifications/")


def orders(order_id="", options=False):
    opt = "/options" if options else ""
    return base.with_path(f"{opt}/orders/{order_id}/")

def password_reset():
    return API_BASE.with_path("/password_reset/request/")


def portfolios():
    return API_BASE.with_path("/portfolios/")


def positions(options=False):
    opt = "/options" if options else ""
    return API_BASE.with_path("{opt}/positions/")


def quotes():
    return API_BASE.with_path("/quotes/")


def historicals(options=False):
    if options:
        return API_BASE.with_path(f"/marketdata/options/historicals/")
    return API_BASE.with_path(f"/quotes/historicals/")


def document_requests():
    return API_BASE.with_path("/upload/document_requests/")


def user():
    return API_BASE.with_path("/user/")


def watchlists():
    return API_BASE.with_path("/watchlists/")


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


def convert_token():
    return API_BASE.with_path("/oauth2/migrate_token/")
