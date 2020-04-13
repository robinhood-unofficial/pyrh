"""Exceptions: custom exceptions for library"""


class PyrhException(Exception):
    """Wrapper for custom robinhood library exceptions."""

    pass


class InvalidCacheFile(PyrhException):
    """Error when the cache config file is found to be invalid."""

    pass


class AuthenticationError(PyrhException):
    """Error when trying to login to robinhood."""

    pass


class InvalidTickerSymbol(PyrhException):
    """When an invalid ticker (stock symbol) is given/"""

    pass


class InvalidInstrumentId(PyrhException):
    """When an invalid instrument id is given/"""

    pass


class InvalidOptionId(PyrhException):
    """When an invalid option id is given/"""

    pass
