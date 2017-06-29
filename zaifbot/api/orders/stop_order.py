class _StopOrder(_Order, _OrderThreadRoutine):
    def __init__(self, currency_pair, action, stop_price, amount, comment=''):
        super().__init__(comment)
        self._currency_pair = CurrencyPair(currency_pair)
        self._action = action
        self._stop_price = stop_price
        self._amount = amount
        self._thread = None
        self._stop_event = Event()

    @property
    def name(self):
        return 'StopOrder'

    @property
    def info(self):
        self._info = super().info
        self._info['currency_pair'] = str(self._currency_pair)
        self._info['action'] = self._action
        self._info['amount'] = self._amount
        self._info['stop_price'] = self._stop_price
        return self._info

    def make_order(self, trade_api):
        self._thread = Thread(target=self._run, args=(trade_api,), daemon=True)
        self._thread.start()
        return self

    def _execute(self, trade_api):
        return _MarketOrder(str(self._currency_pair), self._action, self._amount, self._comment).make_order(trade_api)

    def _can_execute(self):
        if self._action is TRADE_ACTION[0]:
            return self.__is_price_higher_than_stop_price()
        else:
            return self.__is_price_lower_than_stop_price()

    def __is_price_higher_than_stop_price(self):
        return self._currency_pair.last_price()['last_price'] > self._stop_price

    def __is_price_lower_than_stop_price(self):
        return self._currency_pair.last_price()['last_price'] > self._stop_price < self._stop_price

    @property
    def is_alive(self):
        return not self._stop_event.is_set()

    def stop(self):
        self._stop_event.set()