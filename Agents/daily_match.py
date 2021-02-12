# A simple parser that holds for a week
import datetime
import Agents.Environment
from Agents.AgentException import AgentException
from Helpers.stock_info import get_quote_FMP

# An internal ID for use with the profiles, so as to link them
AGENT_ID = "daily_match"
DISPLAY_NAME = "Match Each Day"


def get_orders(new_tickers, existing_tickers, limit, profile_info):
    """Retrieves the stocks that should be examined against the strategy.
    Input: An array-like of stock symbols as strings, a list of tuples of current tickers, and a cash limit
    Output: A dictionary containing buy/sell orders"""
    if type(new_tickers) != list:
        raise TypeError("new_tickers is malformed")
    if type(existing_tickers) != list:
        raise TypeError("existing_tickers is malformed")

    if "AGENT_API_KEY" not in profile_info:
        raise AgentException("This agent requires \"AGENT_API_KEY\" to be defined in the profile")

    orders = {"buy": [], "sell": []}
    weekday = datetime.datetime.today().weekday()
    if weekday < 5:
        # Weekday
        prices = update_prices(new_tickers, profile_info)

        # Step 1: Clear our old tickers that are not desired anymore
        for ticker, count, percent_change in existing_tickers:
            if ticker not in new_tickers:
                orders["sell"].append((ticker, count))

        # Step 2: Figure out how many of each share to buy and place them
        orders["buy"] = calculate_buy(new_tickers, prices, limit)
    return orders


def calculate_buy(tickers, prices, limit):
    # Calculate how many of each share to buy
    buy_list = tickers.copy()
    buy = []
    ready = False
    limit_per = -1
    while not ready:
        limit_per = (float(limit) / len(buy_list)) * .95
        ready = True
        for ticker in buy_list.copy():
            if ticker not in prices:
                buy_list.remove(ticker)
                ready = False
                continue
            if prices[ticker] > limit_per:
                buy_list.remove(ticker)
                ready = False
    # "Buy" each share
    for ticker in buy_list:
        buy.append((ticker, limit_per // prices[ticker]))

    return buy


def update_prices(tickers, profile_info):
    data = {}
    for ticker in tickers:
        raw = get_quote_FMP(ticker, profile_info["AGENT_API_KEY"])
        data[ticker] = raw[0]["price"]
    return data


Agents.Environment.AGENT_LIST[AGENT_ID] = get_orders
Agents.Environment.DISPLAY_NAMES[AGENT_ID] = DISPLAY_NAME