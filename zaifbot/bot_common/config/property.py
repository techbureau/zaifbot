class ApiKeys:
    def __init__(self, config_json):
        self._api_keys = config_json['api_keys']

    @property
    def key(self):
        return self._api_keys['key']

    @property
    def secret(self):
        return self._api_keys['secret']


class System:
    def __init__(self, config_json):
        self._system = config_json['system']
        self._socket = _Socket(config_json)

    @property
    def sleep_time(self):
        return self._system['sleep_time']

    @property
    def currency_pair(self):
        return self._system['currency_pair']

    @property
    def api_domain(self):
        return self._system['api_domain']

    @property
    def retry_count(self):
        return self._system['retry_count']

    @property
    def socket(self):
        return self._socket


class Event:
    def __init__(self, config_json):
        self._loss_cut = _LossCut(config_json)
        self._additional_purchase = _AdditionalPurchase(config_json)

    @property
    def loss_cut(self):
        return self._loss_cut

    @property
    def additional_purchase(self):
        return self._additional_purchase


class _LossCut:
    def __init__(self, config_json):
        self._loss_cut = config_json['event']['loss_cut']

    @property
    def target_value(self):
        return self._loss_cut['target_value']


class _AdditionalPurchase:
    def __init__(self, config_json):
        self._additional_purchase = config_json['event']['additional_purchase']

    @property
    def target_value(self):
        return self._additional_purchase['target_value']


class _Socket:
    def __init__(self, config_json):
        self._socket = config_json['system']['socket']

    @property
    def port(self):
        return self._socket['port']
