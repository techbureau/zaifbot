from flask import Flask, jsonify
from zaifbot.utils.observer import Observer
from threading import Thread, RLock
from zaifbot.logger import bot_logger


class ZaifBot(Flask, Observer):
    def __init__(self, import_name):
        super().__init__(import_name)
        self._strategies = []
        self._trade_threads = dict()
        self._process_info = dict()
        self._lock = RLock()

    def register_strategy(self, strategy):
        self._strategies.append(strategy)

    def start(self, *, sec_wait=1, host=None, port=None, debug=None, **options):
        for strategy in self._strategies:
            strategy.register_observers(self)

            trade_thread = Thread(target=strategy.start, kwargs={'sec_wait': sec_wait})
            trade_thread.daemon = True
            trade_thread.start()
            self._trade_threads[strategy.id_] = trade_thread

        # 子スレッドが死んだら全部殺す。
        # サーバーが止まったらスレッドを殺す。
        super().run(host, port, debug, **options)

    @property
    def process_info(self):
        with self._lock:
            return self._process_info

    def update(self, strategy, *args, **kwargs):
        with self._lock:
            self.process_info[strategy.id_] = strategy.have_position
            #bot_logger.info(strategy.have_position)

app = ZaifBot(__name__)


@app.route('/', methods=['GET'])
def info():
    res = jsonify(app.process_info)
    return res


