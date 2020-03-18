import six


if six.PY3:
    from pyrh.robinhood import Robinhood  # noqa
else:
    from pyrh import Robinhood  # noqa
    import exceptions as RH_exception  # noqa

# TODO: when python2 is dropped fix the noqas
