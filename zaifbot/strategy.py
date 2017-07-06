class Strategy:
    def __init__(self, trade_api, entry_rule, exit_rule, stop_rule=None, filter_rule=None):
        self._trade_api = trade_api
        self._entry_rule = entry_rule
        self._exit_rule = exit_rule
        self._stop_rule = stop_rule
        self._filter_rule = filter_rule
        self._trade = None

    def entry(self):
        self._entry_rule.entry(self._trade_api)

    def exit(self):
        self._exit_rule.exit(self._trade_api, self._trade)

    def stop(self):
        pass

    def start(self):
        while True:
            pass


if __name__ == '__main__':
    from zaifbot.rules.entry.entry import Entry
    from zaifbot.rules.exit.exit import Exit
    from zaifbot.wrapper import BotTradeApi

    class MyEntry(Entry):
        def can_entry(self):
            if self._currency_pair.last_price() > 100000:
                return True

        def entry(self):
            self._api.trade(currency_pair=self)


    my_entry = MyEntry(currency_pair='xem_jpy', amount=100, api=BotTradeApi(key='', secret=''))

    class MyExit(Exit):
        def can_exit(self, trade):
            pass

        def exit(self, trade_api, trade):
            pass

    my_exit = Exit()
    my_strategy = Strategy(my_entry, my_exit)
