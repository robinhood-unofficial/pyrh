"""Exceptions: custom exceptions for library"""


class PyrhException(Exception):
    """Wrapper for custom robinhood library exceptions."""

    pass


class PyrhValueError(ValueError, PyrhException):
    """Value Error for the pyrh library."""


class InvalidCacheFile(PyrhException):
    """Error when the cache config file is found to be invalid."""

    pass


class InvalidOperation(PyrhException):
    """An invalid operation was requsted to be performed."""

    pass


class AuthenticationError(PyrhException):
    """Error when trying to login to robinhood."""

    pass


class InvalidTickerSymbol(PyrhException):
    """When an invalid ticker (stock symbol) is given/"""

    pass


class InvalidOptionId(PyrhException):
    """When an invalid option id is given/"""

    pass
