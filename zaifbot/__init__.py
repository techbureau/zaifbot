import os, sys, subprocess

from zaifbot.errors import ZaifBotError


__version__ = '0.0.5'


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


def install_ta_lib():
    if sys.platform.startswith('linux'):
        cwd = os.path.join(os.path.dirname(__file__), './setup')
        subprocess.call(["./install_ta_lib.sh"], cwd=cwd)
        return

    if sys.platform.startswith('darwin'):
        subprocess.call(["brew", "install", "ta-lib"])
        return

    if sys.platform.startswith('win'):
        bits = '32' if sys.maxsize < 2 ** 31 else '64'
        py_version = str(sys.version_info.major) + str(sys.version_info.minor)
        __install_talib_for_windows(bits, py_version)
        return

    raise ZaifBotError('zaifbot does not support your platform')


def __install_talib_for_windows(bits, py_version):
    if bits == '32':
        file = os.path.join(os.path.dirname(__file__),
                            "setup/TA_Lib-0.4.10-cp{v}-cp{v}m-win32.whl".format(v=py_version))
    else:
        file = os.path.join(os.path.dirname(__file__),
                            "setup/TA_Lib-0.4.10-cp{v}-cp{v}m-win_amd64.whl".format(v=py_version))

    if os.path.isfile(file):
        subprocess.call(["pip", "install", file])
        return

    raise ZaifBotError('zaifbot does not support your platform')