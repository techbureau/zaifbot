from time import time
from zaifapi.impl import ZaifPrivateApi
from zaifbot.bot_common.config import load_config
from zaifbot.bot_common.api import ZaifLastPrice
from zaifbot.bot_common.save_trade_log import save_trade_log
from zaifbot.bot_common.logger import logger


def get_current_last_price(currency_pair):
    api = ZaifLastPrice()
    return api.last_price(currency_pair)


class ZaifOrder:
    def __init__(self):
        self._config = load_config()
        self._private_api = ZaifPrivateApi(self._config.api_keys.key, self._config.api_keys.secret)

    def get_active_orders(self):
        try:
            return self._private_api.active_orders(currency_pair=self._config.system.currency_pair,
                                                   is_token_both=True)
        except Exception:
            return {}

    def trade(self, action, price, amount, limit=None):
        try:
            if limit:
                self._private_api.trade(currency_pair=self._config.system.currency_pair,
                                        action=action,
                                        price=price,
                                        amount=amount,
                                        limit=limit)
                trade_log = {
                    'time': time(),
                    'action': action,
                    'currency_pair': self._config.system.currency_pair,
                    'price': price,
                    'amount': amount,
                    'limit': limit
                    }
            else:
                self._private_api.trade(currency_pair=self._config.system.currency_pair,
                                        action=action,
                                        price=price,
                                        amount=amount)
                trade_log = {
                    'time': time(),
                    'action': action,
                    'currency_pair': self._config.system.currency_pair,
                    'price': price,
                    'amount': amount
                    }
            save_trade_log(trade_log)
        except Exception as e:
            logger.error(e)

    def cancel_order(self, order_id):
        try:
            self._private_api.cancel_order(order_id=order_id)
        except Exception:
            False

    def get_last_trade_history(self):
        try:
            return self._private_api.trade_history(currency_pair=self._config.system.currency_pair,
                                                   order='DESC',
                                                   count=1)
        except Exception as e:
            return e
