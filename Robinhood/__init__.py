import six


if six.PY3:
    from Robinhood.Robinhood import Robinhood  # noqa
else:
    from Robinhood import Robinhood  # noqa
    import exceptions as RH_exception  # noqa

# TODO: when python2 is dropped fix the noqas
