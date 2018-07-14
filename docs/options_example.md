# Options

## Getting trade history

```py
from pprint import pprint
from Robinhood import Robinhood

# authenticate
my_trader = Robinhood()
my_trader.login(username="YOUR_USERNAME", password="YOUR_PASSWORD")

# fetch history
my_option_trades = my_trader.options_order_history()
pprint(my_option_trades)
```
