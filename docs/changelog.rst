.. _changelog:

Changelog
#########

.. towncrier release notes start

Pyrh 2.0.1 (2022-11-25)
=====================

Features
--------

- Add SessionManager to handle oauth and refresh (#215)
- Add marshmallow support for internal models. (#223)
- Added Robinhood watchlists API integration to retrieve watchlist details (stocks) of given authenticated user. (#225)
- Add Instruments model to the project. (#227)


Bugfixes
--------

- Set default challenge method to sms, email no longer works (83c03133b4fc7a8845de2ae1093136973fe988ce)
- Updated the .get_historical_quotes() to use the URL method .with_query() in order to build a URL with params. (#229)
- Fix the options functions. (#235)
- Fix bug in cancel_order due to wrong concatenation syntax. (#296)


Misc
----

- #226


Pyrh 2.0 (2022-11-25)
=====================

Features
--------

- Add SessionManager to handle oauth and refresh (#215)
- Add marshmallow support for internal models. (#223)
- Added Robinhood watchlists API integration to retrieve watchlist details (stocks) of given authenticated user. (#225)
- Add Instruments model to the project. (#227)


Bugfixes
--------

- Set default challenge method to sms, email no longer works (83c03133b4fc7a8845de2ae1093136973fe988ce)
- Updated the .get_historical_quotes() to use the URL method .with_query() in order to build a URL with params. (#229)
- Fix the options functions. (#235)
- Fix bug in cancel_order due to wrong concatenation syntax. (#296)


Misc
----

- #226


pyrh 2.0 (2020-03-18)
=====================
- Fixed 2fa connection issues
- Last version to support python 2

pyrh 1.0.1 (2017-11-07)
=======================
- Added custom exception
