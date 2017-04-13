class Config:
    def __init__(self, system, api_keys, event):
        self.system = system
        self.api_keys = api_keys,
        self.event = event


class System:
    def __init__(self):
        self.sleep_time = 1
        self.api_domain = "api.zaif.jp"
        self.currency_pair = "btc_jpy"
        self.retry_count = 5
        self.socket.port = 8888


class ApiKeys:
    def __init__(self):
        self.key = "api_key"
        self.secret = "secret"


class Event:
    def __init__(self):
        self.buy.target_value = 110000
        self.sell.target_value = 110000