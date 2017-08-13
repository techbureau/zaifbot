from collections import OrderedDict
import itertools
from flask import Flask, jsonify
from zaifbot.utils.observer import Observer
from threading import Thread, RLock
import datetime


class ActiveStrategyInfo:
    def __init__(self, strategy):
        self._started = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self._strategy = strategy
        self._info = OrderedDict()

    def update(self):
        self._info['alive'] = self._strategy.alive
        self._info['position'] = self._strategy.have_position
        self._info['trade_counts'] = self._strategy.total_trades_counts
        self._info['total_profit'] = self._strategy.total_profit

    @property
    def info(self):
        self._info['id_'] = self._strategy.id_
        self._info['name'] = self._strategy.name
        self._info['started'] = self._started
        self._info['alive'] = self._strategy.alive
        self._info['action'] = self._strategy.entry_rule.action.name
        self._info['amount'] = self._strategy.entry_rule.amount
        self._info['entry_rule'] = self._strategy.entry_rule.name
        self._info['exit_rule'] = self._strategy.exit_rule.name
        self._info['position'] = self._strategy.have_position
        self._info['trade_counts'] = self._strategy.total_trades_counts
        self._info['profit'] = self._strategy.total_profit
        return self.info


class _ActiveTradesObserver(Observer):
    def __init__(self):
        self._lock = RLock()
        self._info = OrderedDict()
        self._active_strategies_list = list()
        self._info['active_trades'] = self._active_strategies_list

    @property
    def info(self):
        with self._lock:
            return self._info

    def update(self, strategy):
        with self._lock:
            target = self._find_strategy_info(strategy.id_)
            target.update()

    def add_strategy(self, strategy):
        active_strategy = ActiveStrategyInfo(strategy)
        self._active_strategies_list.append(active_strategy)

    def _find_strategy_info(self, id_):
        strategy = list(filter(lambda strategy_info: strategy_info['id_'] == id_, self._active_strategies_list))[0]
        return strategy


class _ZaifBotApp(Flask):
    def __init__(self, import_name):
        super().__init__(import_name)
        self._strategies = []
        self._trade_threads = dict()
        self._trades_observer = _ActiveTradesObserver()

    def register_strategies(self, strategy, *strategies):
        for strategy in itertools.chain((strategy,), strategies):
            self._strategies.append(strategy)

    def start(self, *, sec_wait=1, host=None, port=None, debug=None, **options):
        for strategy in self._strategies:
            strategy.register_observers(self._trades_observer)

            trade_thread = Thread(target=strategy.start,
                                  kwargs={'sec_wait': sec_wait})
            trade_thread.daemon = True
            self._trade_threads[strategy.id_] = trade_thread
            self._trades_observer.add_strategy(strategy)
            trade_thread.start()

        # stop server when all thread is gone
        # stop all thread when server has some problem
        super().run(host, port, debug, **options)

    @property
    def trading_info(self):
        return self._trades_observer.info

    def update(self, active_strategy):
        self._trades_observer.update(active_strategy)


def zaifbot(import_name):
    app = _ZaifBotApp(import_name)
    app.config['JSON_SORT_KEYS'] = False

    @app.route('/', methods=['GET'])
    def info():
        res = jsonify(app.trading_info)
        return res

    return app
