import time

from zaifbot.api.wrapper import BotPublicApi
from zaifbot.price.cache import ZaifCurrencyPairs
from zaifbot.price.stream import ZaifLastPrice


# TODO: このメソッドはOhlcPricesに持たせるべきメソッド
def get_price_info(currency_pair, period='1d', count=5, to_epoch_time=None):
    to_epoch_time = int(time.time()) if to_epoch_time is None else to_epoch_time
    public_api = BotPublicApi()
    second_api_params = {'period': period, 'count': count, 'to_epoch_time': to_epoch_time}
    return public_api.everything('ohlc_data', currency_pair, second_api_params)


# TODO: 以下のメソッドたちもどこかのクラスに所属させたい
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
    rounded_amount = amount - (amount % currency_pair_info['item_unit_step'])
    digits = len(str(currency_pair_info['item_unit_step'])) - 2
    return round(rounded_amount, digits)


def _get_currency_pair_info(currency_pair):
    currency_pair_infos = ZaifCurrencyPairs()
    return currency_pair_infos[currency_pair]
