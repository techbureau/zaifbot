import time
from zaifbot.utils.observable import Observable
from zaifbot.exchange.api.http import BotTradeApi
from zaifbot.trade.trade import Trade
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
        self.name = name
        self.id_ = None

    def _need_stop(self):
        if self.stop_rule:
            trade_logger.info('check stop', extra={'strategy_ident': self._id_for_log()})
            return self.stop_rule.need_stop(self._trade)

    def _entry(self):
        new_trade = self._create_new_trade(self.id_, self.name)
        self._trade = self.entry_rule.entry(new_trade)
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

        trade_logger.info('process started', extra={'strategy_ident': self._id_for_log()})

        try:
            while self.alive:
                if self._need_stop():
                    self.stop()
                    continue

                trade_logger.info('process alive', extra={'strategy_ident': self._id_for_log()})
                self.regular_job()
                
                if self.have_position:
                    trade_logger.info('check exit', extra={'strategy_ident': self._id_for_log()})
                    self._check_exit()
                else:
                    trade_logger.info('check entry', extra={'strategy_ident': self._id_for_log()})
                    self._check_entry()
                time.sleep(sec_wait)
            else:
                trade_logger.info('process will stop', extra={'strategy_ident': self._id_for_log()})
        except Exception as e:
            trade_logger.exception(e)
            trade_logger.info('exception occurred, process will stop', extra={'strategy_ident': self._id_for_log()})
            self.stop()
        finally:
            # todo: deal in the case of forced termination
            trade_logger.info('process stopped', extra={'strategy_ident': self._id_for_log()})

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

    def _id_for_log(self):
        if self.name:
            return self.name
        if self.id_:
            return self.id_[:12]
        return ''

    @staticmethod
    def _create_new_trade(id_, name):
        new_trade = Trade()
        new_trade.strategy_name = name
        new_trade.process_id = id_
        return new_trade
