from zaifbot.trading_strategy import Strategy
from zaifbot.web import BotTradeApi
from zaifbot.tools import preset_keys
from zaifbot.rules.entry.buy_lower_entry import BuyLowerEntry
from zaifbot.rules.exit.sell_higher_exit import SellHigherExit

"""
値段が低くなったら購入し、高くなったら売るだけの取引です

dealing that buy when price goes down, sell price goes up
"""

preset_keys(key='your_key',
            secret='your_secret')

trade_api = BotTradeApi()
entry_rule = BuyLowerEntry(amount=100, buy_price=0.2)
exit_rule = SellHigherExit(exit_price=0.3)

my_strategy = Strategy(currency_pair='zaif_jpy', entry_rule=entry_rule, exit_rule=exit_rule, trade_api=trade_api)
my_strategy.start()
