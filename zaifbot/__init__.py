from sys import platform
import subprocess
import zipfile


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
    if platform == "linux" or platform == "linux2":
        subprocess.call(["setup/install_ta_lib.sh"])
    elif platform == "win32":
        with zipfile.ZipFile("setup/ta-lib-0.4.0-msvc.zip", "r") as zip_ref:
            zip_ref.extractall("C:\\ta-lib")
