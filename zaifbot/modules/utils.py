from zaifbot.modules.api.last_price import ZaifLastPrice
from zaifbot.modules.api.cache import ZaifCurrencyPairs


def get_current_last_price(currency_pair):
    api = ZaifLastPrice()
    return api.last_price(currency_pair)


def get_round_last_price(currency_pair, *, is_buy):
    return _round_price(currency_pair, get_current_last_price(), is_buy=is_buy)


def get_buyable_amount(currency_pair, amount, price):
    buyable_amount = amount / price
    return _round_amount(currency_pair, buyable_amount)


def _round_price(currency_pair, price, *, is_buy):
    currency_pair_info = _get_currency_pair_info(currency_pair)
    if is_buy:
        return price['last_price'] + \
               (currency_pair_info['aux_unit_step'] -
                (price['last_price'] % currency_pair_info['aux_unit_step']))
    else:
        return price['last_price'] - \
               (price['last_price'] % currency_pair_info['aux_unit_step'])


def _round_amount(currency_pair, amount):
    currency_pair_info = _get_currency_pair_info(currency_pair)
    return amount - (amount % currency_pair_info['item_unit_step'])


def _get_currency_pair_info(currency_pair):
    currency_pair_infos = ZaifCurrencyPairs()
    return currency_pair_infos[currency_pair]
