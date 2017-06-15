from zaifbot.price.cache import ZaifCurrencyPairs
from zaifbot.price.stream import ZaifLastPrice


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
    return amount - (amount % currency_pair_info['item_unit_step'])


def _get_currency_pair_info(currency_pair):
    currency_pair_infos = ZaifCurrencyPairs()
    return currency_pair_infos[currency_pair]
