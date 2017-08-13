from collections import OrderedDict
import itertools
from flask import Flask, jsonify
from zaifbot.utils.observer import Observer
from threading import Thread, RLock
import datetime


class _ActiveTradesInfo:
    def __init__(self):
        self._value = OrderedDict()
        self._active_trades_info = list()
        self._value['active_trades'] = self._active_trades_info

    @property
    def value(self):
        return self._value

    def update(self, strategy):
        id_ = strategy.id_
        target = list(filter(lambda strategy_info: strategy_info['id_'] == id_, self._active_trades_info))[0]
        target['alive'] = strategy.alive
        target['position'] = strategy.have_position
        target['trade_counts'] = strategy.total_trades_counts
        target['total_profit'] = strategy.total_profit

    def append(self, strategy):
        strategy_info = OrderedDict()
        strategy_info['id_'] = strategy.id_
        strategy_info['alive'] = strategy.alive
        strategy_info['position'] = strategy.have_position
        strategy_info['trade_counts'] = strategy.total_trades_counts
        strategy_info['total_profit'] = strategy.total_profit
        strategy_info['started'] = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        strategy_info['strategy'] = OrderedDict()
        strategy_info['strategy']['name'] = strategy.name
        strategy_info['strategy']['currency_pair'] = strategy.entry_rule.currency_pair.name
        strategy_info['strategy']['action'] = strategy.entry_rule.action.name
        strategy_info['strategy']['amount'] = strategy.entry_rule.amount
        strategy_info['strategy']['entry_rule'] = strategy.entry_rule.name
        strategy_info['strategy']['exit_rule'] = strategy.exit_rule.name
        self._active_trades_info.append(strategy_info)


class _ZaifBotApp(Flask, Observer):
    def __init__(self, import_name):
        super().__init__(import_name)
        self._strategies = []
        self._trade_threads = dict()
        self._trading_info = _ActiveTradesInfo()
        self._lock = RLock()

    def register_strategies(self, strategy, *strategies):
        for strategy in itertools.chain((strategy, ), strategies):
            self._strategies.append(strategy)

    def start(self, *, sec_wait=1, host=None, port=None, debug=None, **options):
        for strategy in self._strategies:
            strategy.register_observers(self)

            trade_thread = Thread(target=strategy.start,
                                  kwargs={'sec_wait': sec_wait})
            trade_thread.daemon = True

            self._trade_threads[strategy.id_] = trade_thread
            self._trading_info.append(strategy)

            trade_thread.start()

        # stop server when all thread is gone
        # stop all thread when server has some problem
        super().run(host, port, debug, **options)

    @property
    def trading_info(self):
        with self._lock:
            return self._trading_info.value

    def update(self, active_strategy):
        with self._lock:
            self._trading_info.update(active_strategy)


def zaifbot(import_name):
    app = _ZaifBotApp(import_name)
    app.config['JSON_SORT_KEYS'] = False

    @app.route('/', methods=['GET'])
    def info():
        res = jsonify(app.trading_info)
        return res

    return app
