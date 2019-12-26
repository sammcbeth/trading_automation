from secrets import API_KEY
import requests as req
import json

def get_last_price(ticker):
    baseUrl = f'https://api.polygon.io/v1/last/stocks/{ticker.upper()}?apiKey={API_KEY}'
    data = req.get(baseUrl).text
    data = json.loads(data)
    return data['last']['price']