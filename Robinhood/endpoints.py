def login():
    return "https://api.robinhood.com/api-token-auth/"

def logout():
    return "https://api.robinhood.com/api-token-logout/"

def investment_profile():
    return "https://api.robinhood.com/user/investment_profile/"

def accounts():
    return "https://api.robinhood.com/accounts/"

def ach(option):
    '''
    Combination of 3 ACH endpoints. Options include:
        * iav
        * relationships
        * transfers
    '''
    return "https://api.robinhood.com/ach/iav/auth/" if option == "iav" else "https://api.robinhood.com/ach/{_option}/".format(_option=option)

def applications():
    return "https://api.robinhood.com/applications/"

def dividends():
    return "https://api.robinhood.com/dividends/"

def edocuments():
    return "https://api.robinhood.com/documents/"

def instruments(instrumentId=None, option=None):
    '''
    Return information about a specific instrument by providing its instrument id. 
    Add extra options for additional information such as "popularity"
    '''
    return "https://api.robinhood.com/instruments/" + ("{id}/".format(id=instrumentId) if instrumentId else "") + ("{_option}/".format(_option=option) if option else "")

def margin_upgrades():
    return "https://api.robinhood.com/margin/upgrades/"

def markets():
    return "https://api.robinhood.com/markets/"

def notifications():
    return "https://api.robinhood.com/notifications/"

def orders(orderId=None):
    return "https://api.robinhood.com/orders/" + ("{id}/".format(id=orderId) if orderId else "")

def password_reset():
    return "https://api.robinhood.com/password_reset/request/"

def portfolios():
    return "https://api.robinhood.com/portfolios/"

def positions():
    return "https://api.robinhood.com/positions/"

def quotes():
    return "https://api.robinhood.com/quotes/"

def historicals():
    return "https://api.robinhood.com/quotes/historicals/"

def document_requests():
    return "https://api.robinhood.com/upload/document_requests/"

def user():
    return "https://api.robinhood.com/user/"

def watchlists():
    return "https://api.robinhood.com/watchlists/"

def news(stock):
    return "https://api.robinhood.com/midlands/news/{_stock}/".format(_stock=stock)

def fundamentals(stock):
    return "https://api.robinhood.com/fundamentals/{_stock}/".format(_stock=stock)

def tags(tag=None):
    '''
    Returns endpoint with tag concatenated.
    '''
    return "https://api.robinhood.com/midlands/tags/tag/{_tag}/".format(_tag=tag)

def chain(instrumentid):
    return "https://api.robinhood.com/options/chains/?equity_instrument_ids={_instrumentid}".format(_instrumentid=instrumentid)

def options(chainid, dates, option_type):
    return "https://api.robinhood.com/options/instruments/?chain_id={_chainid}&expiration_dates={_dates}&state=active&tradability=tradable&type={_type}".format(_chainid=chainid, _dates=dates, _type=option_type)

def market_data(optionid):
    return "https://api.robinhood.com/marketdata/options/{_optionid}/".format(_optionid=optionid)

def convert_token():
    return "https://api.robinhood.com/oauth2/migrate_token/"