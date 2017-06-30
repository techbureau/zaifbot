import sys
import subprocess
import os
from zaifbot.bot_common.errors import ZaifBotError


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


# Todo:　ひどすぎる
def install_ta_lib():
    parent_path = os.path.dirname(os.path.abspath(__file__))
    os.chdir(parent_path + "/setup")
    if sys.platform.startswith('linux'):
        subprocess.call(["./install_ta_lib.sh"])
    elif sys.platform.startswith('mac'):
        # todo: 実装
        pass
    elif sys.platform.startswith('win'):
        bits = '32' if sys.maxsize < 2 ** 31 else '64'
        pyv = str(sys.version_info.major) + str(sys.version_info.minor)
        if bits == 32:
            file = os.path.join(os.path.dirname(__file__),
                                "setup/TA_Lib-0.4.10-cp{v}-cp{v}m-win32.whl".format(v=pyv))
            if os.path.isfile(file):
                subprocess.call(["pip", "install", file])
            else:
                raise ZaifBotError('this library does not  support your platform')

        else:
            file = os.path.join(os.path.dirname(__file__),
                                "setup/TA_Lib-0.4.10-cp{v}-cp{v}m-win_amd64.whl".format(v=pyv))
            if os.path.isfile(file):
                subprocess.call(["pip", "install", file])
            else:
                raise ZaifBotError('this library does not  support your platform')
