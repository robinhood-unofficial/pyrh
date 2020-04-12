"""Exceptions: custom exceptions for library"""


class RHException(Exception):
    """Wrapper for custom robinhood library exceptions."""

    pass


class AuthenticationError(RHException):
    """Error when trying to login to robinhood."""

    pass


class InvalidTickerSymbol(RHException):
    """When an invalid ticker (stock symbol) is given/"""

    pass


class InvalidInstrumentId(RHException):
    """When an invalid instrument id is given/"""

    pass


class InvalidOptionId(RHException):
    """When an invalid option id is given/"""

    pass
