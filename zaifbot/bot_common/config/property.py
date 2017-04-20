class System:
    def __init__(self, currency_pair='btc_jpy'):
        self._system = {'currency_pair': currency_pair}

    @property
    def currency_pair(self):
        return self._system['currency_pair']

    @currency_pair.setter
    def currency_pair(self, pair):
        self._system['currency_pair'] = pair
