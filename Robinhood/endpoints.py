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
    if(option == "iav"):
        return "https://api.robinhood.com/ach/iav/auth/"
    else:
        return "https://api.robinhood.com/ach/{_option}/".format(_option=option)

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
    return "https://api.robinhood.com/instruments/{id}/{_option}/".format(id=instrumentId, _option=option) if option else "https://api.robinhood.com/instruments/{id}/".format(id=instrumentId) 

def margin_upgrades():
    return "https://api.robinhood.com/margin/upgrades/"

def markets():
    return "https://api.robinhood.com/markets/"

def notifications():
    return "https://api.robinhood.com/notifications/"

def orders():
    return "https://api.robinhood.com/orders/"

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

def news():
    return "https://api.robinhood.com/midlands/news/"

def fundamentals():
    return "https://api.robinhood.com/fundamentals/"

def tags(tag=None):
    '''
    Returns endpoint with tag concatenated.
    '''
    return "https://api.robinhood.com/midlands/tags/tag/{_tag}/".format(_tag=tag)