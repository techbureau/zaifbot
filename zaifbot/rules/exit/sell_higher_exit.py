from zaifbot.rules.exit import Exit


class SellHigherExit(Exit):
    def __init__(self, trade_api, exit_price):
        super().__init__(trade_api)
        self._exit_price = exit_price

    def can_exit(self, trade):
        return self._exit_price > trade.currency_pair.last_price()
