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
buy = 'buy'
sell = 'sell'


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
        tracked_price = self.get_last_price(tracked_ticker)
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
                time.sleep(60)

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
        if positions:
            entry_price  = positions[0].avg_entry_price
            avg_entry_price = ''
            for price in entry_price:
                avg_entry_price += price
            avg_entry_price = float(avg_entry_price)
            ticker = positions[0].symbol
            symbol = ''
            for letter in ticker:
                symbol += letter
            symbol = str(symbol)
            quantity = positions[0].qty
            qty = ''
            for num in quantity:
                qty += num
            qty = int(qty)
        
        if not positions:
            return self.look_for_buy(tracked_data)
        else:
            return self.look_for_sell(avg_entry_price, symbol, qty, tracked_data=tracked_data)
        
    def look_for_buy(self, tracked_data):
        """ Based upon the assumption that the account does not currently
        hold any position the function monitiors the tracked symbol and price
        for a buying opportunity.
        """
        print('looking for buy')
        print(tracked_data)
        ticker  = tracked_data['tracked_ticker']
        price  = tracked_data['tracked_price']
        current_price = self.get_last_price(ticker)
        print(ticker, current_price)
        if current_price >= 1.005*price:
            self.submit_order(symbol=ticker, side=buy, qty=50000//current_price)
            tracked_data['tracked_price'] = self.get_last_price(ticker)
            return tracked_data
        elif current_price <= .995*price:
            if ticker == OILU:
                current_price = self.get_last_price(OILD)
                self.submit_order(symbol=OILD, side=buy, qty=50000//current_price)
                tracked_data['tracked_price'] = self.get_last_price(OILD)
                tracked_data['tracked_ticker'] = OILD
            else:
                current_price = self.get_last_price(OILU)
                self.submit_order(symbol=OILU, side=buy, qty=50000//current_price)
                tracked_data['tracked_price'] = self.get_last_price(OILU)
                tracked_data['tracked_ticker'] = OILU
            return tracked_data
        else:
            return tracked_data


    def look_for_sell(self, entry_price, symbol, qty, tracked_data):
        """ Based upon the account currently having positions the function monitors
        the current price of positions and looks for a sell opportunity.
        """
        print('looking for sell')
        print(symbol, entry_price)
        latest_price = self.get_last_price(ticker=symbol)
        print(symbol, latest_price)
        if latest_price >= entry_price*1.005:
            self.submit_order(symbol=symbol, side=sell, qty=qty)
            tracked_ticker = symbol
            tracked_price = self.get_last_price(symbol)
            return {'tracked_ticker':tracked_ticker, 'tracked_price':tracked_price}
        elif latest_price <= entry_price*.995:
            self.submit_order(symbol=symbol, side=sell, qty=qty)
            if symbol == OILD:
                tracked_ticker = OILU
            else:
                tracked_ticker = OILD
            tracked_price = self.get_last_price(tracked_ticker)
            return {'tracked_ticker':tracked_ticker, 'tracked_price':tracked_price}
        else:
            return tracked_data
        


    def get_last_price(self, ticker):
        baseUrl = f'https://api.polygon.io/v1/last/stocks/{ticker.upper()}?apiKey={API_KEY}'
        try:
            data = req.get(baseUrl).text
            data = json.loads(data)
            if data['last']['price']:
                return data['last']['price']
            else:
                print('Failed to fetch price data. Sleeping and trying again')
                time.sleep(60)
                self.get_last_price(ticker)
        except:
            print('Failed to fetch price data. Sleeping and trying again')
            time.sleep(60)
            self.get_last_price(ticker)



    # Submit an order if quantity is above 0.
    def submit_order(self, qty, symbol, side):
        if(qty > 0):
            try:
                self.alpaca.submit_order(symbol, qty, side, "market", "day")
                print("Market order of | " + str(qty) + " " + symbol + " " + side + " | completed.")
            except:
                print("Order of | " + str(qty) + " " + symbol + " " + side + " | did not go through.")


 
# Run the Momentum class
TA = Momentum()
TA.run()