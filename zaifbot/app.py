import uuid
import itertools
from flask import Flask, jsonify
from zaifbot.utils.observer import Observer
from threading import Thread, RLock
from zaifbot.logger import bot_logger


class ZaifBot(Flask, Observer):
    def __init__(self, import_name):
        super().__init__(import_name)
        self._strategies = []
        self._trade_threads = dict()
        self._trading_info = dict()
        self._lock = RLock()

    def register_strategies(self, strategy, **strategies):
        for strategy in itertools.chain((strategy, ), strategies):
            self._strategies.append(strategy)

    def start(self, *, sec_wait=1, host=None, port=None, debug=None, **options):
        for strategy in self._strategies:
            strategy.register_observers(self)

            strategy_id = self._get_id()
            trade_thread = Thread(target=strategy.start,
                                  kwargs={'sec_wait': sec_wait, 'id_': strategy_id})
            trade_thread.daemon = True
            trade_thread.start()

            self._trade_threads[strategy_id] = trade_thread

        # stop server when all thread is gone
        # stop all thread when server has some problem
        super().run(host, port, debug, **options)

    @property
    def trading_info(self):
        with self._lock:
            return self._trading_info

    def update(self, active_strategy):
        with self._lock:
            self.trading_info[active_strategy.id_] = active_strategy.have_position

    @staticmethod
    def _get_id():
        return uuid.uuid4().hex

app = ZaifBot(__name__)


@app.route('/', methods=['GET'])
def info():
    res = jsonify(app.trading_info)
    return res


