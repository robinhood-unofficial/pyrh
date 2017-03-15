import six

if six.PY3:
    from Robinhood.Robinhood import Robinhood
else:
    from Robinhood import Robinhood
    import Robinhood.RobinhoodException as RobinhoodException
    import Robinhood.LoginFailed as LoginFailed
    import TwoFactorRequired.TwoFactorRequired as TwoFactorRequired
