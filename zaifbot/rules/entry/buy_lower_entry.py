from zaifbot.exchange.latest_price import get_latest_price
from zaifbot.rules.entry import Entry
from zaifbot.logger import trade_logger


class BuyLowerEntry(Entry):
    def __init__(self, amount, buy_price):
        super().__init__(amount=amount, action='bid')
        self.buy_price = buy_price

    def can_entry(self):
        # fixme: 消す
        trade_logger.info(get_latest_price(self.currency_pair))

        return get_latest_price(self.currency_pair) < self.buy_price
