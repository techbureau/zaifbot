import time
from zaifbot.exchange.api.http import BotTradeApi
from zaifbot.logger import trade_logger


class Strategy:
    # todo: able to handle multiple rules
    def __init__(self, entry_rule, exit_rule, stop_rule=None):
        self._trade_api = BotTradeApi()
        self._entry_rule = entry_rule
        self._exit_rule = exit_rule
        self._stop_rule = stop_rule
        self._trade = None
        self._have_position = False
        self._alive = False

    def _need_stop(self):
        if self._stop_rule:
            trade_logger.info('check stop')
            return self._stop_rule.need_stop(self._trade)

    def _entry(self):
        self._trade = self._entry_rule.entry()
        self._have_position = True

    def _exit(self):
        self._exit_rule.exit(self._trade)
        self._trade = None
        self._have_position = False

    def _check_entry(self):
        if self._entry_rule.can_entry():
            self._entry()

    def _check_exit(self):
        if self._exit_rule.can_exit(self._trade):
            self._exit()

    def start(self, *, sec_wait=1):
        self._alive = True
        trade_logger.info('process started')

        try:
            while self._alive:
                if self._need_stop():
                    self.stop()
                    continue

                trade_logger.info('process alive')
                self.regular_job()
                
                if self._have_position:
                    trade_logger.info('check exit')
                    self._check_exit()
                else:
                    trade_logger.info('check entry')
                    self._check_entry()
                time.sleep(sec_wait)
            else:
                trade_logger.info('process will stop')
        finally:
            # todo: deal in the case of forced termination
            trade_logger.info('process stopped')

    def regular_job(self):
        pass

    def stop(self):
        self._alive = False
