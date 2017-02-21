from zaifbot.bot_common.config import load_config
from zaifbot.modules.auto_trade import *


class ZaifBot:
    _process_funcs = {}

    def set_process_func(self, process_name, func, is_started=None):
        tmp = {
            'func': func
        }
        if is_started is not None:
            tmp['is_started'] = is_started
        self._process_funcs[process_name] = tmp

    def start(self):
        processes = []
        for process_name, func_info in self._process_funcs.items():
            process_obj = self._get_process_factory(process_name, func_info)
            process_obj.start()
            processes.append(process_obj)
        [x.join() for x in processes]

    @staticmethod
    def _get_process_factory(process_name, func_info):
        if process_name == 'loss_cut':
            return LossCut(func_info['func'])
        if process_name == 'additional_purchase':
            return AdditionalPurchase(func_info['func'])
        return Custom(process_name, func_info['func'], func_info['is_started'])
