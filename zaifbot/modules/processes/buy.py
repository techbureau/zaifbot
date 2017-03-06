from abc import abstractmethod
from zaifbot.bot_common.utils import get_current_last_price
from zaifbot.modules.processes.process_common import ProcessBase
from zaifbot.bollinger_bands import get_bollinger_bands
from zaifbot.bot_common.bot_const import PERIOD_SECS
from time import sleep, time


class BuyByPrice(ProcessBase):
    def get_name(self):
        return 'buy_by_price'

    def is_started(self):
        last_price = get_current_last_price()
        if last_price <= self.config.event.buy.target_value:
            return True
        return False

    @abstractmethod
    def execute(self):
        raise NotImplementedError


class BuyByBollingerBands(ProcessBase):
    __BuyByBollingerBands_continue = False
    __BuyByBollingerBands_active = False

    def __init__(self, length, active=True, continue_=False):
        super().__init__()
        self._length = length
        BuyByBollingerBands._BuyByBollingerBands__continue = continue_
        BuyByBollingerBands._BuyByBollingerBands__active = active

    def get_name(self):
        return 'buy_by_bolinger_bands'

    def is_started(self):
        last_price = get_current_last_price()
        bollinger_bands = get_bollinger_bands(
            self.config.system.currency_pair,
            self.config.system.sleep_time,
            1,
            int(time()),
            self._length
        )
        if BuyByBollingerBands._BuyByBollingerBands__active\
                and last_price <= bollinger_bands['return']['bollinger_bands'][0]['sd2n']:
            if BuyByBollingerBands._BuyByBollingerBands__continue:
                BuyByBollingerBands._BuyByBollingerBands__active = False
                #SellByBollingerBands.__SellByBollingerBands_active = True
            return True
        return False

    def run(self):
        while True:
            sleep(PERIOD_SECS[self.config.system.sleep_time])
            if self.is_started() is False:
                continue
            self.execute()


    @abstractmethod
    def execute(self):
        raise NotImplementedError
