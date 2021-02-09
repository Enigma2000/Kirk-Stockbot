import requests

SCHEMA = "https"
ENDPOINT_PAPER = "paper-api.alpaca.markets"
ENDPOINT_LIVE = "api.alpaca.markets"


class PaperTrader:
    def __init__(self, profile_info):
        self.key = profile_info["PAPER_API_KEY"]
        self.secret = profile_info["PAPER_API_SECRET"]
        self.initial = profile_info["INITIAL_VALUE"]
        self._profile_info = profile_info
        self.fetch_properties()

    def fetch_properties(self):
        headers = {"APCA-API-KEY-ID": self.key, "APCA-API-SECRET-KEY": self.secret}
        api_url = "{0}://{1}/v2/account".format(SCHEMA, ENDPOINT_PAPER)
        r = requests.get(api_url, headers=headers)
        json_payload = r.json()

        # Mirror API properties
        for key in json_payload:
            self.__dict__[key] = json_payload[key]

    def buy_symbol(self, symbol, count, type="market", time_in_force="day"):
        body = {
            "symbol": symbol,
            "qty": count,
            "side": "buy",
            "type": type,
            "time_in_force": time_in_force
        }
        headers = {"APCA-API-KEY-ID": self.key, "APCA-API-SECRET-KEY": self.secret}
        api_url = "{0}://{1}/v2/orders".format(SCHEMA, ENDPOINT_PAPER)
        r = requests.post(api_url, headers=headers, json=body)
        return None #r.json()['status']=='accepted'

    def sell_symbol(self, symbol, count, type="market", time_in_force="day"):
        body = {
            "symbol": symbol,
            "qty": count,
            "side": "sell",
            "type": type,
            "time_in_force": time_in_force
        }
        headers = {"APCA-API-KEY-ID": self.key, "APCA-API-SECRET-KEY": self.secret}
        api_url = "{0}://{1}/v2/orders".format(SCHEMA, ENDPOINT_PAPER)
        r = requests.post(api_url, headers=headers, json=body)
        return None#r.json()['status']=='accepted'

    def execute_orders(self, order_list):
        sell_orders = order_list["sell"]
        buy_orders = order_list["buy"]
        statuses = {"accepted":0, "not accepted": 0}
        for symbol, count in sell_orders:
            if self.sell_symbol(symbol, int(count)):
                statuses["accepted"] += 1
            else:
                statuses["not accepted"] += 1
        for symbol, count in buy_orders:
            if self.buy_symbol(symbol, int(count)):
                statuses["accepted"] += 1
            else:
                statuses["not accepted"] += 1
        return statuses

    def get_positions(self):
        headers = {"APCA-API-KEY-ID": self.key, "APCA-API-SECRET-KEY": self.secret}
        api_url = "{0}://{1}/v2/positions".format(SCHEMA, ENDPOINT_PAPER)
        r = requests.get(api_url, headers=headers)
        positions = [(position["symbol"], position["qty"]) for position in r.json()]
        return positions
