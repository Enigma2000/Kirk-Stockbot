# A template for creating a parser
import Parsers.Environment
from Parsers.ParserException import ParserException

# An internal ID for use with the profiles, so as to link them
PARSER_ID = "template_model"
DISPLAY_NAME = "Template"


def get_tickers(profile_info):
    """Retrieves the stocks that should be examined against the strategy.
    Input: A dictionary with relevant endpoint information in profile
    Output: An array-like that contains strings representing the stock symbols"""
    if type(profile_info) != dict:
        raise TypeError("profile_info is malformed")
    raise NotImplementedError("This is a template model")


Parsers.Environment.PARSER_LIST[PARSER_ID] = get_tickers
Parsers.Environment.DISPLAY_NAMES[PARSER_ID] = DISPLAY_NAME
