from decimal import Decimal


class Tick:
    def __init__(self, currency_pair):
        self.size = Decimal(str(currency_pair.info['aux_unit_step']))
        self._decimal_digits = currency_pair.info['aux_unit_point']

    def truncate_price(self, price):
        price = Decimal(str(price))

        remainder = price % self.size
        truncated_price = price - remainder
        if self._decimal_digits == 0:
            return int(truncated_price)
        return float(truncated_price)
