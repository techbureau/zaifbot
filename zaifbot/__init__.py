from sys import platform
import subprocess
import os


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
    parent_path = os.path.dirname(os.path.abspath(__file__))
    os.chdir(parent_path + "/setup")
    if platform == "linux" or platform == "linux2":
        subprocess.call(["./install_ta_lib.sh"])
    elif platform == "win32":
        subprocess.call(["pip", "install", "setup/TA_Lib-0.4.10-cp36-cp36m-win32.whl"])
    elif platform == "win64":
        subprocess.call(["pip", "install", "setup/TA_Lib-0.4.10-cp36-cp36m-win_amd64.whl"])
