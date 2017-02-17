from zaifbot.bot_common.config import load_config
from zaifbot.modules.auto_trade.process import *


def start_auto_trade_daemon():
    config = load_config()
    processes = []

    if config.event.loss_cut.executable:
        loss_cut = LossCut()
        loss_cut.start()
        processes.append(loss_cut)

    [x.join() for x in processes]
