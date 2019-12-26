from src.get_market_data import get_last_price
from src.submit_
import alpaca_trade_api as tradeapi
from secrets import API_KEY, API_SECRET, APCA_API_BASE_URL


OILU = 'OILU'
OILD = 'OILD'


def momentum():
    alpaca = tradeapi.REST(API_KEY, API_SECRET, APCA_API_BASE_URL, 'v2')

    orders = alpaca.list_orders(status="open")
        for order in orders:
            alpaca.cancel_order(order.id)
    
    positions = alpaca.list_positions()
    if positions:
        look_for_sell(positions[0]['avg_entry_price'], positions[0]['symbol'])
    look_for_buy()

def look_for_sell(entry_price, symbol):
    latest_price = get_last_price(symbol)
    if latest_price >= entry_price*1.01:


def look_for_buy():