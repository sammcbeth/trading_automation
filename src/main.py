import alpaca_trade_api as tradeapi
from secrets import API_KEY, API_SECRET, APCA_API_BASE_URL
from market_open import market_open
from submit_order import submit_order
from get_market_data import get_last_price
from momentum import momentum
import threading
import time
import datetime





class TradingAlgo:
    def __init__(self):
        self.alpaca = tradeapi.REST(API_KEY, API_SECRET, APCA_API_BASE_URL, 'v2')

    def run(self, algo, tickers):
        # First, cancel any existing orders so they don't impact our buying power.
        orders = self.alpaca.list_orders(status="open")
        for order in orders:
            self.alpaca.cancel_order(order.id)

        # Wait for market to open.
        print("Waiting for market to open...")
        market_open(self)
        print("Market opened.")
        tracked_ticker = tickers[0]
        tracked_price = get_last_price(tracked_ticker)
        tracked_data = {'tracked_ticker':tracked_ticker, 'tracked_price':tracked_price}
        # Rebalance the portfolio every minute, making necessary trades.
        while True:

            # Figure out when the market will close so we can prepare to sell beforehand.
            clock = self.alpaca.get_clock()
            closingTime = clock.next_close.replace(tzinfo=datetime.timezone.utc).timestamp()
            currTime = clock.timestamp.replace(tzinfo=datetime.timezone.utc).timestamp()
            self.timeToClose = closingTime - currTime

            if(self.timeToClose < (60 * 15)):
                # Close all positions when 15 minutes til market close.
                print("Market closing soon.  Closing positions.")

                positions = self.alpaca.list_positions()
                for position in positions:
                    qty = abs(int(float(position.qty)))
                    submit_order(qty,position.symbol,side='sell')

                # Run script again after market close for next trading day.
                print("Sleeping until market close (15 minutes).")
                time.sleep(60 * 16)
                break
            else:
                # Rebalance the portfolio.
                tracked_data = algo(tracked_data)
                time.sleep(10)

ta = TradingAlgo()
ta.run(momentum, ['OILU','OILD'])