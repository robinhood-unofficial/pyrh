BASE_API = "https://api.robinhood.com"


def login():
    return BASE_API + "/oauth2/token/"


def logout():
    return BASE_API + "/oauth2/revoke_token/"


def investment_profile():
    return BASE_API + "/user/investment_profile/"


def accounts():
    return BASE_API + "/accounts/"


def ach(option):
    """
    Combination of 3 ACH endpoints. Options include:
        * iav
        * relationships
        * transfers
    """
    return (
        BASE_API + "/ach/iav/auth/" if option == "iav" else BASE_API + f"/ach/{option}/"
    )


def applications():
    return BASE_API + "/applications/"


def dividends():
    return BASE_API + "/dividends/"


def edocuments():
    return BASE_API + "/documents/"


def instruments(instrument_id, option):
    """
    Return information about a specific instrument by providing its instrument id.
    Add extra options for additional information such as "popularity"
    """
    return BASE_API + f"/instruments/{instrument_id}/{option}/"


def margin_upgrades():
    return BASE_API + "/margin/upgrades/"


def markets():
    return BASE_API + "/markets/"


def notifications():
    return BASE_API + "/notifications/"


def orders(order_id=""):
    return BASE_API + f"/orders/{order_id}"


def password_reset():
    return BASE_API + "/password_reset/request/"


def portfolios():
    return BASE_API + "/portfolios/"


def positions():
    return BASE_API + "/positions/"


def quotes():
    return BASE_API + "/quotes/"


def historicals():
    return BASE_API + "/quotes/historicals/"


def document_requests():
    return BASE_API + "/upload/document_requests/"


def user():
    return BASE_API + "/user/"


def watchlists():
    return BASE_API + "/watchlists/"


def news(stock):
    return BASE_API + f"/midlands/news/{stock}/"


def fundamentals(stock):
    return BASE_API + f"/fundamentals/{stock}/"


def tags(tag):
    """
    Returns endpoint with tag concatenated.
    """
    return BASE_API + f"/midlands/tags/tag/{tag}/"


def chain(instrument_id):
    return BASE_API + f"/options/chains/?equity_instrument_ids={instrument_id}"


def options(chain_id, dates, option_type):
    return (
        BASE_API
        + f"/options/instruments/?chain_id={chain_id}&expiration_dates={dates}"
        + f"&state=active&tradability=tradable&type={option_type}"
    )


def market_data(option_id):
    return BASE_API + f"/marketdata/options/{option_id}/"


def convert_token():
    return BASE_API + "/oauth2/migrate_token/"
