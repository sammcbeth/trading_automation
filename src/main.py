import alpaca_trade_api as tradeapi
from secrets import API_KEY, API_SECRET, APCA_API_BASE_URL
from market_open import market_open
from submit_order import submit_order
from trading_algos.momentum import momentum
import threading
import time
import datetime





class TradingAlgo:
    def __init__(self):
        self.alpaca = tradeapi.REST(API_KEY, API_SECRET, APCA_API_BASE_URL, 'v2')

    def run(self, algo):
        # First, cancel any existing orders so they don't impact our buying power.
        orders = self.alpaca.list_orders(status="open")
        for order in orders:
            self.alpaca.cancel_order(order.id)

        # Wait for market to open.
        print("Waiting for market to open...")
        market_open(self)
        print("Market opened.")

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
                    respSO = []
                    submit_order(self,qty,position.symbol,orderSide,respSO)

                # Run script again after market close for next trading day.
                print("Sleeping until market close (15 minutes).")
                time.sleep(60 * 16)
                break
            else:
                # Rebalance the portfolio.
                algo()
                time.sleep(10)

ta = TradingAlgo()
ta.run(momentum)