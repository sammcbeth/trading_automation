import time
import datetime

def market_open(self):
    isOpen = self.alpaca.get_clock().is_open
    while(not isOpen):
        clock = self.alpaca.get_clock()
        openingTime = clock.next_open.replace(tzinfo=datetime.timezone.utc).timestamp()
        currTime = clock.timestamp.replace(tzinfo=datetime.timezone.utc).timestamp()
        timeToOpen = int((openingTime - currTime) / 60)
        print(str(timeToOpen) + " minutes til market open.")
        time.sleep(60)
        isOpen = self.alpaca.get_clock().is_open