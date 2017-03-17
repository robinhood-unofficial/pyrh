"""exceptions: custom exceptions for library"""
class RobinhoodException(Exception):
    """wrapper for custom Robinhood library exceptions"""
    pass
class LoginFailed(RobinhoodException):
    """Unable to login to robinhood"""
    pass
class TwoFactorRequired(LoginFailed):
    """Unable to login thanks to 2FA failure"""
    pass
