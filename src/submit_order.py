from main import ta as account

def submit_order(qty, stock, side):
    if(qty > 0):
      try:
        return account.alpaca.submit_order(stock, qty, side, "market", "day")
      except:
        print("Order of | " + str(qty) + " " + stock + " " + side + " | did not go through.")
    else:
      print(f"Market order of | {str(qty)} {stock} {side} | completed.")