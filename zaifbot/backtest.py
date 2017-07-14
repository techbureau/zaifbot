class BackTest:
    def __init__(self, currency_pair, entry_rule, exit_rule, stop_rule=None):
        self.currency_pair = currency_pair
        self._entry_rule = entry_rule
        self._exit_rule = exit_rule
        self._stop_rule = stop_rule
        self._trade = None
        self._have_position = False

        self.__initialize_rules()

    def __initialize_rules(self):
        self._entry_rule.currency_pair = self.currency_pair

    def _check_entry(self):
        if self._entry_rule.can_entry():
            self._entry()

    def _entry(self):
        pass
