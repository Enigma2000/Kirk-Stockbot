# Module for fetching information about a stock, for ease of use and ease of optimization
import requests

FMP_ENDPOINT = "https://financialmodelingprep.com/api/v3"


def get_top_gainers_FMP(API_KEY):
    params = {
        "apikey": API_KEY
    }
    r = requests.get(url=f"{FMP_ENDPOINT}/stock/gainers", params=params)
    return r.json()


def get_quote_FMP(symbol, API_KEY):
    params = {
        "apikey": API_KEY
    }
    r = requests.get(url=f"{FMP_ENDPOINT}/quote/{symbol}", params=params)
    return r.json()
