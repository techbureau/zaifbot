import os
import sys
import subprocess
from flask import jsonify, redirect
from zaifbot.web.app import ZaifBot
from zaifbot.web.resources import strategies
from zaifbot.errors import ZaifBotError, InvalidRequest


__version__ = '0.0.6'


def zaifbot(import_name):
    app = ZaifBot(import_name)
    app.config['JSON_SORT_KEYS'] = False

    @app.errorhandler(InvalidRequest)
    def handle_invalid_usage(error):
        response = jsonify(error.to_dict())
        response.status_code = error.status_code
        return response

    resources = [strategies.resource]
    for resource in resources:
        app.register_blueprint(resource)

    @app.route('/')
    def root():
        return redirect('/strategies/', code=303)

    return app


# fixme: move to other place
def install_ta_lib():
    if sys.platform.startswith('linux'):
        # fixme
        cwd = os.path.join(os.path.dirname(__file__), 'setup')
        subprocess.call(['tar', '-xzf', 'ta-lib-0.4.0-src.tar.gz'], cwd=cwd)
        talib_path = os.path.join(cwd, 'ta-lib')
        subprocess.call(['./configure', '--prefix=/usr'], cwd=talib_path, shell=True)
        subprocess.call(['make'], cwd=talib_path, shell=True)
        subprocess.call(['sudo', 'make', 'install'], cwd=talib_path)
        subprocess.call(['pip', 'install', 'TA-Lib'])
        return

    if sys.platform.startswith('darwin'):
        subprocess.call(["brew", "install", "ta-lib"])
        subprocess.call(['pip', 'install', 'TA-Lib'])
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
