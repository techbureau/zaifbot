from zaifbot import ZaifBot
from zaifbot.modules.auto_trade import *


class MyBuy(Buy):
    def execute(self):
        return True


class MySell(Sell):
    def execute(self):
        return True


class MyCustom(Custom):
    def get_name(self):
        return 'my_custom_process'

    def execute(self):
        return True

    def is_started(self):
        return True


if __name__ == '__main__':
    bot = ZaifBot()
    bot.add_running_process(MyBuy)
    bot.add_running_process(MySell)
    bot.add_running_process(MyCustom)
    bot.start()
