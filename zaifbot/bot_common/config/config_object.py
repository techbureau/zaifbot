class Config:
    def __init__(self, system, api_keys, event):
        self.system = system
        self.api_keys = api_keys,
        self.event = event


class SystemValue:
    def __init__(self):
        self.sleep_time = "1m"
        self.api_domain = "api.zaif.jp"
        self.currency_pair = "btc_jpy"
        self.retry_count = 5
        self.socket = {}
        self.socket['port'] = 8888


class ApiKeysValue:
    def __init__(self):
        self.key = "api_key"
        self.secret = "secret"


class EventValue:
    def __init__(self):
        self.buy = {}
        self.sell = {}
        self.buy['target_value'] = 110000
        self.sell['target_value'] = 110000