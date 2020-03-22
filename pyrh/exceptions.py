"""Exceptions: custom exceptions for library"""


class RobinhoodException(Exception):
    """Wrapper for custom robinhood library exceptions."""

    pass


class AuthenticationError(RobinhoodException):
    """Error when trying to login to robinhood."""

    pass


class LoginFailed(RobinhoodException):  # TODO: Remove me
    """Error when trying to login to robinhood."""

    pass


class InvalidTickerSymbol(RobinhoodException):
    """When an invalid ticker (stock symbol) is given/"""

    pass


class InvalidInstrumentId(RobinhoodException):
    """When an invalid instrument id is given/"""

    pass


class InvalidOptionId(RobinhoodException):
    """When an invalid option id is given/"""

    pass
