import time
from zaifbot.utils import get_unique_trade_api
from zaifbot.currency_pairs import CurrencyPair


class Strategy:
    # todo: ruleを複数持たせられるようにする
    def __init__(self, currency_pair, entry_rule, exit_rule, stop_rule=None, trade_api=None):
        self._trade_api = trade_api or get_unique_trade_api()
        self._currency_pair = CurrencyPair(currency_pair)
        self._entry_rule = entry_rule
        self._exit_rule = exit_rule
        self._stop_rule = stop_rule
        self._trade = None
        self._have_position = False

        self.__initialize_rules()

    def _need_stop(self):
        return self._stop_rule.need_stop()

    def _entry(self):
        self._trade = self._entry_rule.entry()
        self._have_position = True

    def _exit(self):
        self._exit_rule.exit(self._trade)
        self._have_position = False

    def _check_entry(self):
        if self._entry_rule.can_entry():
            self._entry()

    def _check_exit(self):
        if self._exit_rule.can_exit():
            self._exit()

    def start(self, *, sec_wait=1):
        while True:
            if self._need_stop():
                break
            if self._have_position:
                self._check_exit()
            else:
                self._check_entry()
            time.sleep(sec_wait)
        else:
            pass

    def __initialize_rules(self):
        self._entry_rule.trade_api = self._trade_api
        self._entry_rule.currency_pair = self._currency_pair
        self._exit_rule.trade_api = self._trade_api
