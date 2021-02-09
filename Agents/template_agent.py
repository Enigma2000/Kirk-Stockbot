# A template for creating a parser
import Agents.Environment
from Agents.AgentException import AgentException

# An internal ID for use with the profiles, so as to link them
AGENT_ID = "template_model"
DISPLAY_NAME = "Template"


def get_orders(tickers, limit):
    """Retrieves the stocks that should be examined against the strategy.
    Input: An array-like of stock symbols as strings, and a cash limit
    Output: A dictionary containing buy/sell orders"""
    if type(tickers) != list:
        raise TypeError("tickers is malformed")
    raise NotImplementedError("This is a template model")


Agents.Environment.AGENT_LIST[AGENT_ID] = get_orders
Agents.Environment.DISPLAY_NAMES[AGENT_ID] = DISPLAY_NAME
