api_url = "https://api.robinhood.com"

def login():
    return api_url + "/oauth2/token/"

def logout():
    return api_url + "/oauth2/revoke_token/"

def investment_profile():
    return api_url + "/user/investment_profile/"

def accounts():
    return api_url + "/accounts/"

def ach(option):
    '''
    Combination of 3 ACH endpoints. Options include:
        * iav
        * relationships
        * transfers
    '''
    return api_url + "/ach/iav/auth/" if option == "iav" else api_url + "/ach/{_option}/".format(_option=option)

def applications():
    return api_url + "/applications/"

def dividends():
    return api_url + "/dividends/"

def edocuments():
    return api_url + "/documents/"

def instruments(instrumentId=None, option=None):
    '''
    Return information about a specific instrument by providing its instrument id.
    Add extra options for additional information such as "popularity"
    '''
    return api_url + "/instruments/" + ("{id}/".format(id=instrumentId) if instrumentId else "") + ("{_option}/".format(_option=option) if option else "")

def margin_upgrades():
    return api_url + "/margin/upgrades/"

def markets():
    return api_url + "/markets/"

def notifications():
    return api_url + "/notifications/"

def orders(orderId=None):
    return api_url + "/orders/" + ("{id}/".format(id=orderId) if orderId else "")

def password_reset():
    return api_url + "/password_reset/request/"

def portfolios():
    return api_url + "/portfolios/"

def positions():
    return api_url + "/positions/"

def quotes():
    return api_url + "/quotes/"

def historicals():
    return api_url + "/quotes/historicals/"

def document_requests():
    return api_url + "/upload/document_requests/"

def user():
    return api_url + "/user/"

def watchlists():
    return api_url + "/watchlists/"

def news(stock):
    return api_url + "/midlands/news/{_stock}/".format(_stock=stock)

def fundamentals(stock):
    return api_url + "/fundamentals/{_stock}/".format(_stock=stock)

def tags(tag=None):
    '''
    Returns endpoint with tag concatenated.
    '''
    return api_url + "/midlands/tags/tag/{_tag}/".format(_tag=tag)

def chain(instrumentid):
    return api_url + "/options/chains/?equity_instrument_ids={_instrumentid}".format(_instrumentid=instrumentid)

def options(chainid, dates, option_type):
    return api_url + "/options/instruments/?chain_id={_chainid}&expiration_dates={_dates}&state=active&tradability=tradable&type={_type}".format(_chainid=chainid, _dates=dates, _type=option_type)

def market_data(optionid):
    return api_url + "/marketdata/options/{_optionid}/".format(_optionid=optionid)

def convert_token():
    return api_url + "/oauth2/migrate_token/"
