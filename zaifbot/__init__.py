from zaifbot.bot_common.config import load_config


class ZaifBot:
    _process = []

    def add_running_process(self, auto_trade_process):
        self._process.append(auto_trade_process)

    def start(self):
        running_processes = []
        for process in self._process:
            process.start()
            running_processes.append(process)
        [x.join() for x in running_processes]


"""
最初にうる、買うがあり、
その後売る、買うがある
まずはその２種類でいい、スタートのタイミングも見れればベスト
あとWebSocketに対応させる
"""