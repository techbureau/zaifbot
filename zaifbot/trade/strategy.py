import time
from zaifbot.utils.observable import Observable
from zaifbot.exchange.api.http import BotTradeApi
from zaifbot.trade.trade import Trade
from zaifbot.logger import trade_logger


class Strategy(Observable):
    def __init__(self, entry_rule, exit_rule, stop_rule=None, name=None):
        super().__init__()
        self.entry_rule = entry_rule
        self.exit_rule = exit_rule
        self.stop_rule = stop_rule
        self.name = name
        self.id_ = None
        self.total_profit = 0
        self.total_trades_counts = 0

        self._trade_api = BotTradeApi()
        self._trade = None
        self._have_position = False
        self._alive = False

    def start(self, *, sec_wait=1, **options):
        self._before_start(**options)
        self.alive = True
        trade_logger.info('process started',
                          extra={'strategyid': self._descriptor()})

        try:
            self._main_loop(sec_wait)
        except Exception as e:
            trade_logger.exception(e, extra={'strategyid': self._descriptor()})
            trade_logger.error('exception occurred, process will stop',
                               extra={'strategyid': self._descriptor()})
            self.stop()
        finally:
            trade_logger.info('process stopped',
                              extra={'strategyid': self._descriptor()})

    def _main_loop(self, sec_wait):
        while self.alive:
            self._check_stop()
            trade_logger.info('process alive',
                              extra={'strategyid': self._descriptor()})

            self.before_trading_routine()
            self._trading_routine()
            self.after_trading_routine()

            time.sleep(sec_wait)
        else:
            trade_logger.info('process will stop',
                              extra={'strategyid': self._descriptor()})

    def _check_entry(self):
        if self.entry_rule.can_entry():
            self._entry()

    def _check_exit(self):
        if self.exit_rule.can_exit(self._trade):
            self._exit()

    def _check_stop(self):
        if self.stop_rule is None:
            return
        trade_logger.info('check stop',
                          extra={'strategyid': self._descriptor()})
        if self.stop_rule.need_stop(self._trade):
            self.stop()

    def _entry(self):
        new_trade = self._new_trade()
        self._trade = self.entry_rule.entry(new_trade)
        self.have_position = True

    def _exit(self):
        self.exit_rule.exit(self._trade)
        self._add_latest_profit(self._trade.profit())
        self._increase_trade_count()
        self._trade = None
        self.have_position = False

    def _trading_routine(self):
        if self.have_position:
            trade_logger.info('check exit',
                              extra={'strategyid': self._descriptor()})
            self._check_exit()
            return

        trade_logger.info('check entry',
                          extra={'strategyid': self._descriptor()})
        self._check_entry()

    def before_trading_routine(self):
        # for user customize
        pass

    def after_trading_routine(self):
        # for user customize
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

    def _add_latest_profit(self, profit):
        self.total_profit += profit
        self.notify_observers()

    def _increase_trade_count(self):
        self.total_trades_counts += 1
        self.notify_observers()

    def _before_start(self, **options):
        pass

    def _descriptor(self):
        return self.name or self.id_[:12] or ''

    def _new_trade(self):
        new_trade = Trade()
        new_trade.strategy_name = self.name
        new_trade.process_id = self.id_
        return new_trade
