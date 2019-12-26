from get_market_data import get_last_price
from submit_order import submit_order
import alpaca_trade_api as tradeapi
from main import ta as account


OILU = 'OILU'
OILD = 'OILD'


def momentum(tracked_data):

    orders = account.alpaca.list_orders(status="open")
        for order in orders:
            account.alpaca.cancel_order(order.id)
    
    positions = account.alpaca.list_positions()
    if positions:
        look_for_sell(positions[0]['avg_entry_price'], positions[0]['symbol'], positions[0]['qty'])
    look_for_buy(tracked_data)

def look_for_sell(entry_price, symbol, qty, tracked_data):
    """ Based upon the account currently having positions the function monitors
    the current price of positions and looks for a sell opportunity.
    """
    latest_price = get_last_price(symbol=symbol)
    if latest_price >= entry_price*1.005:
        submit_order(symbol=symbol, side=sell, qty=qty)
        if symbol == OILD:
            tracked_ticker = OILD
        else:
            tracked_ticker = OILU
        get_last_price(tracked_ticker)
        return {'tracked_ticker':tracked_ticker, 'tracked_price':tracked_price}
    elif latest_price <= entry_price*.995:
        submit_order(symbol=symbol, side=sell, qty=qty)
        if symbol == OILD:
            tracked_ticker = OILU
        else:
            tracked_ticker = OILD
        get_last_price(tracked_ticker)
        return {'tracked_ticker':tracked_ticker, 'tracked_price':tracked_price}
    else:
        return tracked_data

def look_for_buy(tracked_data):
    """ Based upon the assumption that the account does not currently
    hold any position the function monitiors the tracked symbol and price
    for a buying opportunity.
    """
    ticker  = tracked_data['tracked_ticker']
    price  = tracked_data['tracked_price']
    current_price = get_last_price(ticker)
    if current_price >= 1.005*price:
        submit_order(symbol=ticker, side=buy, qty=50000//price)
    elif current_price <= .995*price:
        if ticker == OILU:
            submit_order(symbol=OILD, side=buy, qty=50000//price)
        else:
            submit_order(symbol=OILU, side=buy, qty=50000//price)
    return tracked_data
