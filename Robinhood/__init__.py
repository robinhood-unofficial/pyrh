import six

if six.PY3:
    from Robinhood.Robinhood import Robinhood
else:
    from Robinhood import Robinhood
