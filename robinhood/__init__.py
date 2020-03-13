import six


if six.PY3:
    from robinhood.robinhood import Robinhood  # noqa
else:
    from robinhood import Robinhood  # noqa
    import exceptions as RH_exception  # noqa

# TODO: when python2 is dropped fix the noqas
