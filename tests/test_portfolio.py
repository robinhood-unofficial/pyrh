from os import path
from datetime import datetime

import pytest
from flaky import flaky

from Robinhood import Robinhood
import Robinhood.exceptions as RH_exception

import helpers

HERE = path.abspath(path.dirname(__file__))
ROOT = path.dirname(HERE)

CONFIG_FILENAME = path.join(HERE, 'test_config.cfg')

CONFIG = helpers.get_config(CONFIG_FILENAME)

LOGIN_OK = False
def test_login_happypath(config=CONFIG):
    """try to log in to Robinhood"""
    global LOGIN_OK

    if (not config.get('LOGIN', 'username')) or (not config.get('LOGIN', 'password')):
        LOGIN_OK = False
        pytest.xfail('no login credentials given')

    try:
        LOGIN_OK = Robinhood().login(
            username=config.get('LOGIN', 'username'),
            password=config.get('LOGIN', 'password')
        )
    except Exception as err_msg:
        LOGIN_OK = False
        raise err_msg

    assert LOGIN_OK

def test_login_badpass(config=CONFIG):
    """try to login with bad creds"""
    if not LOGIN_OK:
        pytest.xfail('cannot test without valid user/passwd')
    bad_pass = 'PASSWORD'
    with pytest.raises(RH_exception.LoginFailed):
        Robinhood().login(
            username=config.get('LOGIN', 'username'),
            password=bad_pass
        )

