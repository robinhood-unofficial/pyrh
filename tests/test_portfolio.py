# from datetime import datetime
# from os import path
#
# import helpers
# import pytest
# import six
# from flaky import flaky
#
# import pyrh.exceptions as RH_exception
# from pyrh import Robinhood
#
#
# if six.PY2:
#     from pyrh import RH_exception
#
#
# HERE = path.abspath(path.dirname(__file__))
# ROOT = path.dirname(HERE)
#
# CONFIG_FILENAME = path.join(HERE, "test_config.cfg")
#
# CONFIG = helpers.get_config(CONFIG_FILENAME)
#
# LOGIN_OK = False
#
#
# def test_login_happypath(config=CONFIG):
#     """try to log in to robinhood"""
#     global LOGIN_OK
#
#     if (not config.get("LOGIN", "username")) or (not config.get("LOGIN", "password")):
#         LOGIN_OK = False
#         pytest.xfail("no login credentials given")
#
#     try:
#         LOGIN_OK = Robinhood().login(
#             username=config.get("LOGIN", "username"),
#             password=config.get("LOGIN", "password"),
#         )
#     except Exception as err_msg:
#         LOGIN_OK = False
#         raise err_msg
#
#     assert LOGIN_OK
#
#
# def test_login_badpass(config=CONFIG):
#     """try to login with bad creds"""
#     if not LOGIN_OK:
#         pytest.xfail("cannot test without valid user/passwd")
#     bad_pass = "PASSWORD"
#     with pytest.raises(RH_exception.LoginFailed):
#         Robinhood().login(username=config.get("LOGIN", "username"), password=bad_pass)
#
#
# TEST_PORTFOLIO = {}
#
#
# @pytest.mark.incremental
# class TestPortfolioMethods:
#     """test wrappers on `portfolio` endpoint
#
#     NOTE: reliant on an active account to pull data from
#
#     """
#
#     rh_obj = Robinhood()
#     try:
#         rh_obj.login(
#             username=CONFIG.get(
#                 "LOGIN", "username"
#             ),  # NOTE: py.test fails w/o password
#             password=CONFIG.get("LOGIN", "password"),
#         )
#     except Exception:
#         pass
#
#     def test_portfolios(self):
#         """check `portfolio` method"""
#         global TEST_PORTFOLIO
#         if not LOGIN_OK:
#             print("Unable to test Portfolio without auth")
#             pytest.xfail("cannot test without valid user/passwd")
#         print(self.rh_obj.auth_token)
#         data = self.rh_obj.portfolios()
#         # TODO validate data
#
#         TEST_PORTFOLIO = data
#
#     def test_validate_adjusted_equity(self):
#         """test `adjusted_equity_previous_close` method"""
#         value = self.rh_obj.adjusted_equity_previous_close()
#         assert isinstance(value, float)
#         assert format(value, ".4f") == TEST_PORTFOLIO["adjusted_equity_previous_close"]
#
#     def test_validate_equity(self):
#         """test `equity` method"""
#         value = self.rh_obj.equity()
#         assert isinstance(value, float)
#         assert format(value, ".4f") == TEST_PORTFOLIO["equity"]
#
#     def test_equity_previous_close(self):
#         """test `equity_previous_close` method"""
#         value = self.rh_obj.equity_previous_close()
#         assert isinstance(value, float)
#         assert format(value, ".4f") == TEST_PORTFOLIO["equity_previous_close"]
#
#     def test_excess_margin(self):
#         """test `excess_margin` method"""
#         value = self.rh_obj.excess_margin()
#         assert isinstance(value, float)
#         assert format(value, ".4f") == TEST_PORTFOLIO["excess_margin"]
#
#     def test_ex_hours_equity(self):
#         """test `extended_hours_equity method"""
#         value = self.rh_obj.extended_hours_equity()
#         assert isinstance(value, float) or (value is None)
#         if value:
#             assert format(value, ".4f") == TEST_PORTFOLIO["extended_hours_equity"]
#
#     def test_ex_hours_market_value(self):
#         """test `extended_hours_market_value` method"""
#         value = self.rh_obj.extended_hours_market_value()
#         assert isinstance(value, float) or (value is None)
#         if value:
#             assert format(value, ".4f") == TEST_PORTFOLIO["extended_hours_market_value"]
#
#     def test_last_core_equity(self):
#         """test `last_core_equity` method"""
#         value = self.rh_obj.last_core_equity()
#         assert isinstance(value, float)
#         assert format(value, ".4f") == TEST_PORTFOLIO["last_core_equity"]
#
#     def test_last_core_market_value(self):
#         """test `last_core_market_value` method"""
#         value = self.rh_obj.last_core_market_value()
#         assert isinstance(value, float)
#         assert format(value, ".4f") == TEST_PORTFOLIO["last_core_market_value"]
#
#     def test_market_value(self):
#         """test `market_value` method"""
#         value = self.rh_obj.market_value()
#         assert isinstance(value, float)
#         assert format(value, ".4f") == TEST_PORTFOLIO["market_value"]
#
#     def test_investment_profile(self):
#         """test `investment_profile` endpoint"""
#         data = self.rh_obj.investment_profile()
#         # TODO: validate keys
#
#     def test_get_account(self):
#         """test `get_account` endpoing"""
#         data = self.rh_obj.get_account()
#         # TODO: validate keys
#
#
# def test_logout(config=CONFIG):
#     """make sure logout works"""
#     if not LOGIN_OK:
#         pytest.xfail("cannot test without valid user/passwd")
#     rh_obj = Robinhood()
#     assert rh_obj.login(
#         username=config.get("LOGIN", "username"),
#         password=config.get("LOGIN", "password"),
#     )
#     assert rh_obj.auth_token is not None
#     req = rh_obj.logout()
#
#     assert req.status_code == 200
#
#
# def test_bad_logout():
#     """logout without logging in"""
#     if not LOGIN_OK:
#         pytest.xfail("cannot test without valid user/passwd")
#     rh_obj = Robinhood()
#     with pytest.warns(UserWarning):
#         req = rh_obj.logout()
#
#     assert req.status_code != 200
#
#
# def test_cancel_bad_order_id():
#     """cancel a naughty order id"""
#     bad_id = "1234Dx"
#     if not LOGIN_OK:
#         pytest.xfail("cannot test without valid user/passwd")
#     rh_obj = Robinhood()
#     rh_obj.login(
#         username=CONFIG.get("LOGIN", "username"),
#         password=CONFIG.get("LOGIN", "password"),
#     )
#     with pytest.raises(ValueError):
#         rh_obj.cancel_order(bad_id)
