from zaifapi import ZaifPublicApi
from zaifbot.bot_common.bot_const import PERIOD_SECS, LIMIT_COUNT
from zaifbot.modules.dao.moving_average import TradeLogsDao, MovingAverageDao
import numpy as np


class TradeLogsManager:
    def __init__(self, currency_pair, period, count, length):
        self._currency_pair = currency_pair
        self._period = period
        self._count = count
        self._length = length
        self._trade_logs = TradeLogsDao(self._currency_pair, self._period)

    def setup(self, start_epoch_time, end_epoch_time):
        target_epoch_times = self._get_target_epoch_times(start_epoch_time, end_epoch_time)
        if len(target_epoch_times) == 0:
            return
        api_records = self._get_ohlc_data_from_server(end_epoch_time)
        target_trade_logs_record = \
            list(filter(lambda x: x['time'] in target_epoch_times, api_records))
        trade_logs_model_dataset = self._set_trade_logs_model_dataset(target_trade_logs_record)
        self._trade_logs.create_data(trade_logs_model_dataset)

    def get_trade_logs_record(self, start_epoch_time, end_epoch_time):
        query_ = self._trade_logs.get_query(end_epoch_time, start_epoch_time, False)
        return self._trade_logs.get_record(query_)

    def _get_target_epoch_times(self, start_epoch_time, end_epoch_time):
        query_ = self._trade_logs.get_query(end_epoch_time, start_epoch_time, True)
        trade_logs_record = self._trade_logs.get_record(query_)
        return self._check_missing_records(
            trade_logs_record, start_epoch_time, end_epoch_time, self._period)

    def _check_missing_records(self, trade_logs_record, start_time, end_time, period):
        to_epoch_times = set([x.time for x in trade_logs_record])
        target_epoch_times = set()
        for need_epoch_time in self._get_need_epoch_times(start_time, end_time, period):
            if need_epoch_time not in to_epoch_times:
                target_epoch_times.add(need_epoch_time)
        return target_epoch_times

    def _set_trade_logs_model_dataset(self, target_trade_logs_record):
        trade_logs_model_dataset = []
        for trade_logs in target_trade_logs_record:
            trade_logs_model_dataset.append(self._trade_logs.model(
                time=trade_logs['time'],
                currency_pair=self._currency_pair,
                period=self._period,
                open=trade_logs['open'],
                high=trade_logs['high'],
                low=trade_logs['low'],
                close=trade_logs['close'],
                average=trade_logs['average'],
                volume=trade_logs['volume'],
                closed=int(trade_logs['closed'])
            ))
        return trade_logs_model_dataset

    @classmethod
    def _get_need_epoch_times(cls, start_time, end_time, period):
        while True:
            yield start_time
            start_time += PERIOD_SECS[period]
            if start_time >= end_time:
                yield end_time
                break

    def _get_ohlc_data_from_server(self, end_epoch_time):
        public_api = ZaifPublicApi()
        api_params = {'period': self._period, 'count': LIMIT_COUNT, 'to_epoch_time': end_epoch_time + 1}
        api_record = public_api.everything('ohlc_data', self._currency_pair, api_params)
        required_count = self._count + self._length
        if required_count <= LIMIT_COUNT:
            return api_record
        count = required_count - LIMIT_COUNT
        second_end_epoch_time = end_epoch_time - (LIMIT_COUNT * PERIOD_SECS[self._period]) + 1
        second_api_params = {'period': self._period, 'count': count, 'to_epoch_time': second_end_epoch_time}
        second_api_record = public_api.everything('ohlc_data', self._currency_pair, second_api_params)
        api_record = second_api_record + api_record
        return api_record


class MovingAverageManager:
    def __init__(self, currency_pair, period, count, length):
        self._currency_pair = currency_pair
        self._period = period
        self._count = count
        self._length = length
        self._moving_average = MovingAverageDao(self._currency_pair, self._period, self._length)

    def setup(self, start_epoch_time, end_epoch_time):
        moving_average_record = self._moving_average.get_record(end_epoch_time, start_epoch_time)
        target_elements = self._check_missing_records(moving_average_record, start_epoch_time, end_epoch_time, self._period)
        if len(target_elements['target_epoch_times']) == 0:
            return
        trade_logs = TradeLogsManager(self._currency_pair, self._period, self._count, self._length)
        trade_logs_record = trade_logs.get_trade_logs_record(start_epoch_time, end_epoch_time)
        moving_average = self._get_moving_average(trade_logs_record, target_elements)
        # target_trade_logs_record = \
        #    list(filter(lambda x: x.time in target_epoch_times, trade_logs_record))
        # moving_average = self._get_moving_average(target_trade_logs_record)
        # moving_average_model_dataset = self._set_moving_average_model_dataset(moving_average)
        # self._moving_average.create_data(moving_average_model_dataset)

    def _get_target_epoch_times(self, moving_average_record):
        return self._check_missing_records(
            moving_average_record, start_epoch_time, end_epoch_time, self._period)

    def _check_missing_records(self, moving_average_record, start_time, end_time, period):
        exist_epoch_times = list([x.time for x in moving_average_record])
        target_epoch_times = []
        last_ema = []
        counter = 0
        for need_epoch_time in TradeLogsManager._get_need_epoch_times(start_time, end_time, period):
            if need_epoch_time not in exist_epoch_times and counter >= self._length:
                target_epoch_times.append(need_epoch_time)
                last_ema.append(self._get_last_ema(moving_average_record, exist_epoch_times, last_epoch_time))
            last_epoch_time = need_epoch_time
            counter = counter + 1
        target_elements = {'target_epoch_times': target_epoch_times, 'last_ema': last_ema}
        return target_elements

    def _get_last_ema(self, moving_average_record, exist_epoch_times, last_epoc_time):
        if last_epoc_time in exist_epoch_times:
            return moving_average_record[exist_epoch_times.index(last_epoc_time)].time
        return None

    def _get_moving_average(self, trade_logs_record, target_elements):
        for record in trade_logs_record:
            if record.time in target_elements['target_epoch_times']:
                nums = self._get_nums()

    def _get_nums(self):
        # sma算出用の値を取得する
        return 0

    '''
    def _get_nums(self, trade_logs_record, i):
        nums = []
        for j in range(0, self._length):
            nums.append(trade_logs_record[i-j])
        return nums

    def _calculate_moving_average(self, nums):
        sma_nums = nums
        ema_nums = nums

        sma_nums.pop(0)
        sma = np.average(sma_nums)

        current_val = pop(ema_nums)
        k = 2 / (self._length + 1)

    def  _calculate_sma(self, nums):
        nums.pop(0)
        return np.average(nums)

    def  _calculate_ema(self, nums):

    def _get_moving_average(self, target_trade_logs_record):
        moving_average = {}
        for i in range(self._length, len(target_trade_logs_record)):
            nums = []
            for x in range(0, self._length):
                nums.append(target_trade_logs_record[i - x].close)
            #print(nums)
    '''
