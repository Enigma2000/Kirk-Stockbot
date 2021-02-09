# A template for creating a parser
import json
import Parsers.Environment
from Parsers.ParserException import ParserException
from Helpers.stock_info import get_top_gainers_FMP

# An internal ID for use with the profiles, so as to link them
PARSER_ID = "financialmodelingprep_topgainers"
DISPLAY_NAME = "Top Gainers - Financial Modeling Prep"


def get_tickers(profile_info):
    """Retrieves the stocks that should be examined against the strategy.
    Input: A dictionary with relevant endpoint information in profile
        - Expected profile_info for this parser: apikey
    Output: An array-like that contains strings representing the stock symbols"""
    if type(profile_info) != dict:
        raise TypeError("profile_info is malformed")
    if "PARSER_API_KEY" not in profile_info:
        raise ParserException("This parser requires \"PARSER_API_KEY\" to be defined in the profile")
    try:
        json_load = get_top_gainers_FMP(profile_info["PARSER_API_KEY"])
        tickers = parse_json(json_load)
    except Exception as e:
        # Unknown generic error
        raise ParserException("Unknown generic error: " + e.args[0])
    return tickers


def parse_json(json_payload):
    """Given a JSON payload matching the last updated API from the site, retrieves all the symbols from the list.
    Input: JSON payload
    Output: Array of strings containing the symbols"""
    tickers_raw = json_payload["mostGainerStock"]
    ticker_list = []
    for entry in tickers_raw:
        ticker_list.append(entry["ticker"])
    return ticker_list


Parsers.Environment.PARSER_LIST[PARSER_ID] = get_tickers
Parsers.Environment.DISPLAY_NAMES[PARSER_ID] = DISPLAY_NAME
