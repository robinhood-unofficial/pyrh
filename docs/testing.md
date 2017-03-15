# Testing Robinhood Library

Using [py.test](http://doc.pytest.org/en/latest/contents.html) to validate coverage and behavior of Robinhood methods.  Devs should feel confident that when they use this library, that their data is being handled properly and reliably, especially when real-money could be on the line.

## Getting Started

* `test_config.cfg` has been included to make adjusting globals easy.  **NOTE DO NOT COMMIT SECRETS** use `test_config_local.cfg` to track secrets like login information
* Don't forget to build a [virtualenv](http://docs.python-guide.org/en/latest/dev/virtualenvs/)
* Coverage is designed to be version-agnostic.  Both Py2/Py3 are covered 
    * requires running in py2 or py3 virtualenv to test

Testing is easy:
> `python setup.py test`

## Notes

* Coverage is included as a review tool, not a requirement
* `@pytest.mark.incremental` allows for sequence/group tests [more info](http://doc.pytest.org/en/latest/example/simple.html#incremental-testing-test-steps)
* Some tests are squishy due to update windows, may require retry loops
    * [flaky](https://pypi.python.org/pypi/flaky) has been included to retry weird tests
* **DO NOT TEST DURING TRADING HOURS** will assert on price data

## TODO

* Add test coverage for [`input()` calls](http://stackoverflow.com/a/35851524)