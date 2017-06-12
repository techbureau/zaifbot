import time
from zaifbot.bot_common.slack_notifier import SlackNotifier
from zaifbot.modules.api.stream import ZaifLastPrice
from zaifbot.modules.api.cache import ZaifCurrencyPairs
from zaifbot.modules.api.wrapper import BotPublicApi


def get_price_info(currency_pair, period='1d', count=5, to_epoch_time=None):
    to_epoch_time = int(time.time()) if to_epoch_time is None else to_epoch_time
    public_api = BotPublicApi()
    second_api_params = {'period': period, 'count': count, 'to_epoch_time': to_epoch_time}
    return public_api.everything('ohlc_data', currency_pair, second_api_params)


def get_current_last_price(currency_pair):
    api = ZaifLastPrice()
    return api.last_price(currency_pair)


def get_more_executable_price(currency_pair, price, *, is_buy):
    currency_pair_info = _get_currency_pair_info(currency_pair)
    if is_buy:
        return price + (currency_pair_info['aux_unit_step'] -
                        (price % currency_pair_info['aux_unit_step']))
    else:
        return price - (price % currency_pair_info['aux_unit_step'])


def get_buyable_amount(currency_pair, amount, price):
    buyable_amount = amount / price
    return get_round_amount(currency_pair, buyable_amount)


def get_round_amount(currency_pair, amount):
    currency_pair_info = _get_currency_pair_info(currency_pair)
    return amount - (amount % currency_pair_info['item_unit_step'])


def _get_currency_pair_info(currency_pair):
    currency_pair_infos = ZaifCurrencyPairs()
    return currency_pair_infos[currency_pair]


def send_slack_message(slack_token, channel_id, message, username):
    slack_notifier = SlackNotifier(slack_token)
    return slack_notifier.send_message(channel_id, message, username)
