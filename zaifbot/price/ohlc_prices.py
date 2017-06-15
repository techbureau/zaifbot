import pandas as pd
from zaifbot.api.wrapper import BotPublicApi
from zaifbot.bot_common.logger import logger
from zaifbot.dao.ohlc_prices import OhlcPricesDao
from zaifbot.bot_common.bot_const import PERIOD_SECS, LIMIT_COUNT
import time


def get_need_epoch_times(start_time, end_time, period):
    while True:
        yield start_time
        start_time += PERIOD_SECS[period]
        if start_time >= end_time:
            yield end_time
            break


def get_price_info(currency_pair, period='1d', count=5, to_epoch_time=None):
    to_epoch_time = int(time.time()) if to_epoch_time is None else to_epoch_time
    public_api = BotPublicApi()
    second_api_params = {'period': period, 'count': count, 'to_epoch_time': to_epoch_time}
    return public_api.everything('ohlc_data', currency_pair, second_api_params)


def check_missing_records(exist_epoch_times, start_time, end_time, period):
    need_epoch_times = \
        set([x for x in get_need_epoch_times(start_time, end_time, period)])
    return need_epoch_times.difference(exist_epoch_times)


class OhlcPrices:
    def __init__(self, currency_pair, period, count, length):
        self._currency_pair = currency_pair
        self._period = period
        self._count = count
        self._length = length
        self._ohlc_prices = OhlcPricesDao(self._currency_pair, self._period)

    def execute(self, start_time, end_time):
        target_epoch_times = pd.DataFrame(index=self._get_target_epoch_times(start_time, end_time))
        if len(target_epoch_times.index) == 0:
            return True
        api_records = pd.DataFrame(self._get_ohlc_data_from_server(end_time))

        if api_records.empty:
            return False
        target_ohlc_prices_record = api_records.join(target_epoch_times, on='time', how='inner')
        target_ohlc_prices_record['currency_pair'] = self._currency_pair
        target_ohlc_prices_record['period'] = self._period
        self._ohlc_prices.create_data(target_ohlc_prices_record)
        return api_records[-(self._count + self._length):][['close', 'closed', 'time']]

    def _get_target_epoch_times(self, start_time, end_time):
        ohlc_prices_record = \
            set(x.time for x in self._ohlc_prices.get_records(end_time, start_time, True))
        return check_missing_records(ohlc_prices_record, start_time, end_time, self._period)

    def _get_ohlc_data_from_server(self, end_time):
        public_api = BotPublicApi()
        api_params = {'period': self._period, 'count': LIMIT_COUNT, 'to_epoch_time': end_time + 1}
        try:
            api_record = public_api.everything('ohlc_data', self._currency_pair, api_params)
        except Exception as e:
            logger.error(e, exc_info=True)
            api_record = []
        required_count = self._count + self._length
        if required_count <= LIMIT_COUNT:
            return api_record
        count = required_count - LIMIT_COUNT
        second_end_time = end_time - (LIMIT_COUNT * PERIOD_SECS[self._period]) + 1
        second_api_params =\
            {'period': self._period, 'count': count, 'to_epoch_time': second_end_time}
        try:
            second_api_record =\
                public_api.everything('ohlc_data', self._currency_pair, second_api_params)
        except Exception as e:
            logger.error(e, exc_info=True)
            second_api_record = []
        api_record = second_api_record + api_record
        return api_record
