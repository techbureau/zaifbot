from flask import Flask
from zaifbot.utils.observer import Observer
from multiprocessing import Process, Lock
from zaifbot.logger import bot_logger
from threading import Thread


class ZaifBot(Flask, Observer):
    def __init__(self, import_name):
        super().__init__(import_name)
        self._strategies = []
        self._process_info = dict()
        self._lock = Lock()

    def register_strategy(self, strategy):
        self._strategies.append(strategy)

    def start(self, *, sec_wait=1, host=None, port=None, debug=None, **options):
        for strategy in self._strategies:
            strategy.register_observers(self)

            p = Thread(target=strategy.start, kwargs={'sec_wait': sec_wait})
            p.daemon = True
            p.start()

        super().run(host, port, debug, **options)

    @property
    def process_info(self):
        with self._lock:
            return self._process_info

    def update(self, strategy, *args, **kwargs):
        with self._lock:
            bot_logger.info(strategy.have_position)
            bot_logger.info('updateeeeeeeeeeeeeeeeeeeeee')

app = ZaifBot(__name__)


@app.route('/', methods=['GET'])
def info():
    return app._process_info


