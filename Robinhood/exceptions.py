"""
    Exceptions: custom exceptions for library
"""


class RobinhoodException(Exception):
    """
        Wrapper for custom Robinhood library exceptions
    """

    pass


class LoginFailed(RobinhoodException):
    """
        Unable to login to Robinhood
    """
    pass


class TwoFactorRequired(LoginFailed):
    """
        Unable to login because of 2FA failure
    """

    pass


class InvalidTickerSymbol(RobinhoodException):
    """
        When an invalid ticker (stock symbol) is given
    """

    pass


class InvalidInstrumentId(RobinhoodException):
    """
        When an invalid instrument id is given
    """
    pass
