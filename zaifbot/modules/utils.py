from zaifbot.modules.api.wrapper import BotTradeApi
from zaifbot.bot_common.logger import logger
from zaifbot.modules.api.last_price import ZaifLastPrice
from zaifbot.modules.api.cache import ZaifCurrencyPairs


def get_current_last_price(currency_pair):
    api = ZaifLastPrice()
    return api.last_price(currency_pair)


def get_bid_amount(currency_pair, from_currency_amount=None, last_price=None):
    last_price = get_current_last_price(currency_pair)['last_price'] if last_price is None else last_price
    currency_pair_info = _get_currency_pair_info(currency_pair)
    amount = from_currency_amount / last_price
    amount = amount - (amount % currency_pair_info['item_unit_step'])
    return amount


def _get_currency_pair_info(currency_pair):
    currency_pair_infos = ZaifCurrencyPairs()
    return currency_pair_infos[currency_pair]

class ZaifOrder:
    def __init__(self, api_key, api_secret):
        self._private_api = BotTradeApi(api_key, api_secret)

    def get_active_orders(self, currency_pair):
        try:
            return self._private_api.active_orders(currency_pair=currency_pair,
                                                   is_token_both=True)
        except Exception:
            return {}

    def trade(self, currency_pair, action, price, amount, limit=None):
        try:
            if limit:
                self._private_api.trade(currency_pair=currency_pair,
                                        action=action,
                                        price=price,
                                        amount=amount,
                                        limit=limit)
            else:
                self._private_api.trade(currency_pair=currency_pair,
                                        action=action,
                                        price=price,
                                        amount=amount)
        except Exception as e:
            logger.error(e)

    def cancel_order(self, order_id):
        try:
            self._private_api.cancel_order(order_id=order_id)
        except Exception:
            False

    def get_last_trade_history(self, currency_pair):
        try:
            return self._private_api.trade_history(currency_pair=currency_pair,
                                                   order='DESC',
                                                   count=1)
        except Exception as e:
            return e

if __name__ == '__main__':
    print(get_current_last_price('btc_jpy'))