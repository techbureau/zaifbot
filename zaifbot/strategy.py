import time


class Strategy:
    def __init__(self, trade_api, entry_rule, exit_rule, stop_rule=None, filter_rule=None):
        self._trade_api = trade_api
        self._entry_rule = entry_rule
        self._exit_rule = exit_rule
        self._stop_rule = stop_rule
        self._filter_rule = filter_rule
        self._trade = None
        self._have_position = False

    def stop(self):
        pass

    def _entry(self):
        self._trade = self._entry_rule.entry(self._trade_api)
        self._have_position = True

    def _exit(self):
        self._exit_rule.exit(self._trade_api, self._trade)
        self._have_position = False

    def _check_entry(self):
        if self._entry_rule.can_entry():
            self._entry()

    def _check_exit(self):
        if self._exit_rule.can_exit():
            self._exit()

    def start(self, *, sec_wait=1):
        while True:
            if self._have_position:
                self._check_exit()
            else:
                self._check_entry()
            time.sleep(sec_wait)

# if __name__ == '__main__':
#     from zaifbot.rules.entry.entry import Entry
#     from zaifbot.rules.exit.exit import Exit
#     from zaifbot.wrapper import BotTradeApi
#
#     class MyEntry(Entry):
#         def can_entry(self):
#             if self._currency_pair.last_price() > 100000:
#                 return True
#
#         def entry(self):
#             self._api.trade(currency_pair=self)
#
#
#     my_entry = MyEntry(currency_pair='xem_jpy', amount=100, action='bid', api=BotTradeApi(key='', secret=''))
#
#     class MyExit(Exit):
#         def can_exit(self, trade):
#             pass
#
#         def exit(self, trade_api, trade):
#             pass
#
#     my_exit = Exit()
#     my_strategy = Strategy(my_entry, my_exit)
#     my_strategy.start(sec_wait=5)
