from zaifbot.bot_common.config import load_config
from zaifbot.modules.auto_trade import *


class ZaifBot:
    _process_funcs = {}

    def set_process_func(self, process_name, func):
        self._process_funcs[process_name] = func

    def start(self):
        processes = []
        for process_name, func in self._process_funcs.items():



        if self._los_cut_func:
            loss_cut = LossCut(self._los_cut_func)
            loss_cut.start()
            processes.append(loss_cut)
        [x.join() for x in processes]

    @staticmethod
    def get_process_factory(process_name):
        if process_name == 'loss_cut':
            return LossCut
        if process_name == 