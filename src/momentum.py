import alpaca_trade_api as tradeapi
import threading
import time
import datetime
import requests as req
import json
from random import choice
from secrets import API_KEY, API_SECRET, APCA_API_BASE_URL


OILD = 'OILD'
OILU = 'OILU'


class Momentum:
    def __init__(self):
        self.alpaca = tradeapi.REST(API_KEY, API_SECRET, APCA_API_BASE_URL, 'v2')
        self.timeToClose = None

    def run(self):
        orders = self.alpaca.list_orders(status="open")
        for order in orders:
            self.alpaca.cancel_order(order.id)

        # Wait for market to open.
        print("Waiting for market to open...")
        self.awaitMarketOpen()
        print("Market opened.")
        tracked_ticker = choice([OILU, OILD])
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
                    self.submit_order(qty,position.symbol,side='sell')

                # Run script again after market close for next trading day.
                print("Sleeping until market close (15 minutes).")
                time.sleep(60 * 16)
                break
            else:
                # Rebalance the portfolio.
                tracked_data = self.algo(tracked_data)
                time.sleep(10)

    # Wait for market to open.
    def awaitMarketOpen(self):
        isOpen = self.alpaca.get_clock().is_open
        while(not isOpen):
            clock = self.alpaca.get_clock()
            openingTime = clock.next_open.replace(tzinfo=datetime.timezone.utc).timestamp()
            currTime = clock.timestamp.replace(tzinfo=datetime.timezone.utc).timestamp()
            timeToOpen = int((openingTime - currTime) / 60)
            print(str(timeToOpen) + " minutes til market open.")
            time.sleep(60)
            isOpen = self.alpaca.get_clock().is_open

    def algo(self, tracked_data):
        positions = self.alpaca.list_positions()
        if not positions:
            return self.look_for_buy(tracked_data)
        else:
            return self.look_for_sell(positions[0]['avg_entry_price'], positions[0]['symbol'], positions[0]['qty'], tracked_data)
        
    def look_for_buy(self, tracked_data):
        """ Based upon the assumption that the account does not currently
        hold any position the function monitiors the tracked symbol and price
        for a buying opportunity.
        """
        ticker  = tracked_data['tracked_ticker']
        price  = tracked_data['tracked_price']
        current_price = get_last_price(ticker)
        if current_price >= 1.005*price:
            submit_order(symbol=ticker, side=buy, qty=50000//price)
            tracked_data['tracked_price'] = get_last_price(ticker)
            return tracked_data
        elif current_price <= .995*price:
            if ticker == OILU:
                submit_order(symbol=OILD, side=buy, qty=50000//price)
                tracked_data['tracked_price'] = get_last_price(OILD)
                tracked_data['tracked_ticker'] = OILD
            else:
                submit_order(symbol=OILU, side=buy, qty=50000//price)
                tracked_data['tracked_price'] = get_last_price(OILU)
                tracked_data['tracked_ticker'] = OILU
            return tracked_data
        else:
            return tracked_data


    def look_for_sell(entry_price, symbol, qty, tracked_data):
        """ Based upon the account currently having positions the function monitors
        the current price of positions and looks for a sell opportunity.
        """
        latest_price = get_last_price(symbol=symbol)
        if latest_price >= entry_price*1.005:
            submit_order(symbol=symbol, side=sell, qty=qty)
            tracked_ticker = symbol
            tracked_price = get_last_price(symbol)
            return {'tracked_ticker':tracked_ticker, 'tracked_price':tracked_price}
        elif latest_price <= entry_price*.995:
            submit_order(symbol=symbol, side=sell, qty=qty)
            if symbol == OILD:
                tracked_ticker = OILU
            else:
                tracked_ticker = OILD
            tracked_price = get_last_price(tracked_ticker)
            return {'tracked_ticker':tracked_ticker, 'tracked_price':tracked_price}
        else:
            return tracked_data
        


    def get_last_price(ticker):
        baseUrl = f'https://api.polygon.io/v1/last/stocks/{ticker.upper()}?apiKey={API_KEY}'
        data = req.get(baseUrl).text
        data = json.loads(data)
        return data['last']['price']


    # Submit an order if quantity is above 0.
    def submitOrder(self, qty, stock, side):
        if(qty > 0):
            try:
                self.alpaca.submit_order(stock, qty, side, "market", "day")
                print("Market order of | " + str(qty) + " " + stock + " " + side + " | completed.")
            except:
                print("Order of | " + str(qty) + " " + stock + " " + side + " | did not go through.")
            else:
                print("Quantity is 0, order of | " + str(qty) + " " + stock + " " + side + " | not completed.")


 
# Run the Momentum class
TA = Momentum()
TA.run()