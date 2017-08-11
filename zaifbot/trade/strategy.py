import time
from zaifbot.utils.observable import Observable
from zaifbot.exchange.api.http import BotTradeApi
from zaifbot.logger import trade_logger


class Strategy(Observable):
    # todo: able to handle multiple rules
    def __init__(self, entry_rule, exit_rule, stop_rule=None, name=None):
        super().__init__()
        self._trade_api = BotTradeApi()
        self.entry_rule = entry_rule
        self.exit_rule = exit_rule
        self.stop_rule = stop_rule
        self._trade = None
        self._have_position = False
        self._alive = False
        self.name = name or self.__class__.__name__
        self.id_ = None

    def _need_stop(self):
        if self.stop_rule:
            trade_logger.info('check stop')
            return self.stop_rule.need_stop(self._trade)

    def _entry(self):
        self._trade = self.entry_rule.entry()
        self.have_position = True

    def _exit(self):
        self.exit_rule.exit(self._trade)
        self._trade = None
        self.have_position = False

    def _check_entry(self):
        if self.entry_rule.can_entry():
            self._entry()

    def _check_exit(self):
        if self.exit_rule.can_exit(self._trade):
            self._exit()

    def start(self, *, sec_wait=1, **options):
        self._before_start(**options)

        self.alive = True

        trade_logger.info('process started')

        try:
            while self.alive:
                if self._need_stop():
                    self.stop()
                    continue

                trade_logger.info('process alive')
                self.regular_job()
                
                if self.have_position:
                    trade_logger.info('check exit')
                    self._check_exit()
                else:
                    trade_logger.info('check entry')
                    self._check_entry()
                time.sleep(sec_wait)
            else:
                trade_logger.info('process will stop')
        except Exception as e:
            trade_logger.exception(e)
            trade_logger.info('exception occurred, process will stop')
            self.stop()
        finally:
            # todo: deal in the case of forced termination
            trade_logger.info('process stopped')

    def regular_job(self):
        pass

    def stop(self):
        self.alive = False

    @property
    def have_position(self):
        return self._have_position

    @have_position.setter
    def have_position(self, boolean):
        self._have_position = boolean
        self.notify_observers()

    @property
    def alive(self):
        return self._alive

    @alive.setter
    def alive(self, boolean):
        self._alive = boolean
        self.notify_observers()

    def _before_start(self, **options):
        pass
