import pandas as pd
import time
from zaifbot.api.wrapper import BotPublicApi
from zaifbot.bot_common.logger import logger
from zaifbot.dao.ohlc_prices import OhlcPricesDao
from zaifbot.bot_common.bot_const import PERIOD_SECS, LIMIT_COUNT
from zaifbot.utils import truncate_time_at_period, calc_start_from_count_and_end


# todo: このメソッドはいづれ消え去る
def get_price_info(currency_pair, period='1d', count=5, to_epoch_time=None):
    to_epoch_time = int(time.time()) if to_epoch_time is None else to_epoch_time
    public_api = BotPublicApi()
    second_api_params = {'period': period, 'count': count, 'to_epoch_time': to_epoch_time}
    return public_api.everything('ohlc_data', currency_pair, second_api_params)


class OhlcPrices:
    def __init__(self, currency_pair, period):
        self._currency_pair = currency_pair
        self._period = period
        self._dao = OhlcPricesDao(self._currency_pair, self._period)

    def fetch_data(self, count=LIMIT_COUNT, to_epoch_time=None):
        count = min(count, LIMIT_COUNT)
        to_epoch_time = to_epoch_time or int(time.time())
        start_time = calc_start_from_count_and_end(count, to_epoch_time, self._period)

        db_records = self._fetch_data_from_db(start_time=start_time, end_time=to_epoch_time)
        if len(db_records) >= count:
            return db_records

        api_records = self._fetch_data_from_web(count, to_epoch_time)
        return api_records

    def _fetch_data_from_web(self, count, to_epoch_time):
        public_api = BotPublicApi()
        api_params = {'period': self._period, 'count': count, 'to_epoch_time': to_epoch_time}
        records = public_api.everything('ohlc_data', self._currency_pair, api_params)
        self._dao.create_data(records)
        return records

    def _fetch_data_from_db(self, start_time, end_time):
        records = list(map(self._row2dict, self._dao.get_records(end_time, start_time, closed=False)))
        return records

    # todo: もっと汎用的な場所に移動させる
    @staticmethod
    def _row2dict(row):
        dict_row = row.__dict__
        dict_row.pop('_sa_instance_state', None)
        return dict_row
