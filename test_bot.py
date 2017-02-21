from zaifbot import ZaifBot


def los_cut_func(config):
    pass


def additional_purchase_func(config):
    pass


def custom_process_func(config):
    pass


def custom_process_is_start(config):
    pass


if __name__ == '__main__':
    bot = ZaifBot()
    bot.set_process_func('loss_cut', los_cut_func)
    bot.set_process_func('additional_purchase', additional_purchase_func)
    bot.set_process_func('custom_process', custom_process_func, custom_process_is_start)
    bot.start()
