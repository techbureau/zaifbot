import uuid
from collections import OrderedDict
import itertools
from flask import Flask, jsonify
from zaifbot.utils.observer import Observer
from threading import Thread, RLock


class ActiveStrategiesInfo:
    def __init__(self):
        self._value = OrderedDict()
        self._strategies_info = list()
        self._value['active_strategies'] = self._strategies_info

    @property
    def value(self):
        return self._value

    def update(self, strategy):
        id_ = strategy.id_
        target = list(filter(lambda strategy_info: strategy_info['id_'] == id_, self._strategies_info))[0]
        target['position'] = strategy.have_position
        target['alive'] = strategy.alive

    def append(self, strategy):
        strategy_info = OrderedDict()
        strategy_info['id_'] = strategy.id_
        strategy_info['entry_rule'] = strategy.entry_rule.name
        strategy_info['exit_rule'] = strategy.exit_rule.name
        self._strategies_info.append(strategy_info)


class ZaifBot(Flask, Observer):
    def __init__(self, import_name):
        super().__init__(import_name)
        self._strategies = []
        self._trade_threads = dict()
        self._trading_info = ActiveStrategiesInfo()
        self._lock = RLock()

    def register_strategies(self, strategy, **strategies):
        for strategy in itertools.chain((strategy, ), strategies):
            self._strategies.append(strategy)

    def start(self, *, sec_wait=1, host=None, port=None, debug=None, **options):
        for strategy in self._strategies:
            strategy.register_observers(self)

            strategy_id = self._get_id()
            strategy.id_ = strategy_id
            trade_thread = Thread(target=strategy.start,
                                  kwargs={'sec_wait': sec_wait})
            trade_thread.daemon = True
            self._trade_threads[strategy_id] = trade_thread
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

    @staticmethod
    def _get_id():
        return uuid.uuid4().hex

app = ZaifBot(__name__)
app.config['JSON_SORT_KEYS'] = False


@app.route('/', methods=['GET'])
def info():
    res = jsonify(app.trading_info)
    return res


