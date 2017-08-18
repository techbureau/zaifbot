import uuid
import datetime
from collections import OrderedDict
from threading import Event, Condition
from zaifbot.trade.trade import Trade
from zaifbot.logger import trade_logger


class Strategy:
    def __init__(self, entry_rule, exit_rule, stop_rule=None, name=None):
        self.entry_rule = entry_rule
        self.exit_rule = exit_rule
        self.stop_rule = stop_rule
        self.name = name
        self.id_ = _generate_id()
        self.total_profit = 0
        self.total_trades_counts = 0
        self.started = None

        self._status = Status()
        self._have_position = Event()
        self._trade = None
        self._cv = Condition()

    @property
    def have_position(self):
        return self._have_position.is_set()

    @property
    def status(self):
        return self._status.status

    def start(self, *, sec_wait=1):
        self.started = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self._status.to_running()
        trade_logger.info('process started',
                          extra={'strategyid': self._descriptor()})
        self._main_loop(sec_wait=sec_wait)

    def get_info(self):
        # much of position
        info = OrderedDict()
        info['id_'] = self.id_
        info['name'] = self.name
        info['started'] = self.started
        info['status'] = self.status
        info['currency_pair'] = self.entry_rule.currency_pair.name
        info['action'] = self.entry_rule.action.name
        info['amount'] = self.entry_rule.amount
        info['entry_rule'] = self.entry_rule.name
        info['exit_rule'] = self.exit_rule.name
        info['position'] = self.have_position
        info['trade_count'] = self.total_trades_counts
        info['profit'] = self.total_profit
        info['id_'] = self.id_
        info['id_'] = self.id_
        return info

    def stop(self):
        if self._status.is_stopped():
            trade_logger.info('process already stopped', extra={'strategyid': self._descriptor()})
            return

        self._status.to_stopped()
        self._wake_up_and_next_loop()

    def pause(self):
        if self._status.is_paused():
            trade_logger.info('process already paused', extra={'strategyid': self._descriptor()})
            return

        self._status.to_paused()
        trade_logger.info('process paused', extra={'strategyid': self._descriptor()})
        self._wake_up_and_next_loop()

    def restart(self):
        if self._status.is_running():
            trade_logger.info('process already running', extra={'strategyid': self._descriptor()})
            return

        self._status.to_running()
        trade_logger.info('process restarted', extra={'strategyid': self._descriptor()})
        self._wake_up_and_next_loop()

    def is_alive(self):
        return self._status.is_alive()

    def _main_loop(self, sec_wait):
        try:
            while self._status.is_alive():
                self._status.wait_until_continuable()

                if self._need_stop():
                    self.stop()
                    break

                trade_logger.info('process running', extra={'strategyid': self._descriptor()})

                self._trading_routine()
                self._sleep(sec_wait)
        except Exception as e:
            trade_logger.exception(e, extra={'strategyid': self._descriptor()})
            trade_logger.error('exception occurred, process will stop',
                               extra={'strategyid': self._descriptor()})
            self.stop()
        finally:
            trade_logger.info('process stopped', extra={'strategyid': self._descriptor()})

    def _check_entry(self):
        trade_logger.info('check entry',
                          extra={'strategyid': self._descriptor()})
        if self.entry_rule.can_entry():
            self._entry()

    def _check_exit(self):
        trade_logger.info('check exit',
                          extra={'strategyid': self._descriptor()})
        if self.exit_rule.can_exit(self._trade):
            self._exit()

    def _need_stop(self):
        if self.stop_rule is None:
            return False
        trade_logger.info('check stop',
                          extra={'strategyid': self._descriptor()})
        return self.stop_rule.need_stop(self._trade)

    def _entry(self):
        new_trade = self._new_trade()
        self._trade = self.entry_rule.entry(new_trade)
        self._have_position.set()

    def _exit(self):
        self.exit_rule.exit(self._trade)
        self._add_latest_profit(self._trade.profit())
        self._increase_trade_count()
        self._trade = None
        self._have_position.clear()

    def _trading_routine(self):
        self._check_exit() if self.have_position else self._check_entry()

    def _add_latest_profit(self, profit):
        self.total_profit += profit

    def _increase_trade_count(self):
        self.total_trades_counts += 1

    def _descriptor(self):
        return self.name or self.id_[:12] or ''

    def _new_trade(self):
        new_trade = Trade()
        new_trade.strategy_name = self.name
        new_trade.process_id = self.id_
        return new_trade

    def _sleep(self, sec_wait):
        with self._cv:
            self._cv.wait(timeout=sec_wait)

    def _wake_up_and_next_loop(self):
        with self._cv:
            self._cv.notify_all()


class Status:
    def __init__(self):
        self._is_alive = Event()
        self._can_continue = Event()
        self._status = 'created'

    def to_created(self):
        self._status = 'created'

    def to_running(self):
        self._is_alive.set()
        self._can_continue.set()
        self._status = 'running'

    def to_stopped(self):
        self._can_continue.clear()
        self._is_alive.clear()
        self._status = 'stopped'

    def to_paused(self):
        self._can_continue.clear()
        self._status = 'paused'

    def is_created(self):
        return self._status == 'created'

    def is_running(self):
        return self._status == 'running'

    def is_stopped(self):
        return self._status == 'stopped'

    def is_paused(self):
        return self._status == 'paused'

    @property
    def status(self):
        return self._status

    def is_alive(self):
        return self._is_alive.is_set()

    def can_continue(self):
        return self._can_continue.is_set()

    def wait_until_continuable(self):
        self._can_continue.wait()


def _generate_id():
    id_ = uuid.uuid4().hex
    return id_
