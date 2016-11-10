import json                                                                                                                                                                                                         
import csv
import shelve

from Robinhood import Robinhood

def get_symbol_from_instrument_url(rb_client, url, db):
    instrument = {}
    if url in db:
        instrument = db[url]
    else:
        db[url] = fetch_json_by_url(rb_client, url)
        instrument = db[url]
    return instrument['symbol']


def fetch_json_by_url(rb_client, url):
    return rb_client.session.get(url).json()


def order_item_info(order, rb_client, db):
    #side: .side,  price: .average_price, shares: .cumulative_quantity, instrument: .instrument, date : .last_transaction_at
    symbol = get_symbol_from_instrument_url(rb_client, order['instrument'], db)
    return {
        'side': order['side'],
        'price': order['average_price'],
        'shares': order['cumulative_quantity'],
        'symbol': symbol,
        'date': order['last_transaction_at'],
        'state': order['state']
    }


def get_all_history_orders(rb_client):
    orders = []
    past_orders = rb.order_history()
    orders.extend(past_orders['results'])
    while past_orders['next']:
        print("{} order fetched".format(len(orders)))
        next_url = past_orders['next']
        past_orders = fetch_json_by_url(rb_client, next_url)
        orders.extend(past_orders['results'])
    print("{} order fetched".format(len(orders)))
    return orders


rb = Robinhood()
# !!!!!! change the username and passs, be careful when paste the code to public 
rb.login(username="name", password="pass")
past_orders = get_all_history_orders(rb)
instruments_db = shelve.open('instruments.db')
orders = [order_item_info(order, rb, instruments_db) for order in past_orders]
keys = ['side', 'symbol', 'shares', 'price', 'date', 'state']
with open('orders.csv', 'w') as output_file:
    dict_writer = csv.DictWriter(output_file, keys)
    dict_writer.writeheader()
    dict_writer.writerows(orders)

