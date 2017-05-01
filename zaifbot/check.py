from zaifbot.bot_common.api.wrapper import BotTradeApi
from zaifbot.bot_common.api.order import AutoCancelClient
import time
KEY = '0732026a-5763-4fff-89c0-4b2f3f073a33'
SECRET = '05d44556-694a-4564-908a-c77a2820c9f0'

trade_api = BotTradeApi(KEY, SECRET)
print(trade_api.active_orders(currency_pair='btc_jpy'))

cancel_client = AutoCancelClient(KEY, SECRET)
cancel_client.cancel_by_price(191025633, currency_pair='btc_jpy', target_margin=5)

# for i in range(10):
#     print(cancel_client.get_active_cancel_orders())
#     time.sleep(1)