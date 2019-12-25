def submit_order(self, qty, stock, side, resp):
    if(qty > 0):
      try:
        self.alpaca.submit_order(stock, qty, side, "market", "day")
        print(f"Market order of | {str(qty)} {stock} {side} | completed.")
        resp.append(True)
      except:
        print("Order of | " + str(qty) + " " + stock + " " + side + " | did not go through.")
        resp.append(False)
    else:
      print("Quantity is 0, order of | " + str(qty) + " " + stock + " " + side + " | not completed.")
      resp.append(True)