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

    def setup(self, start_time, end_time):
        target_epoch_times = self._get_target_epoch_times(start_time, end_time)
        if len(target_epoch_times) == 0:
            return
        api_records = self._get_ohlc_data_from_server(end_time)
        target_trade_logs_record = \
            list(filter(lambda x: x['time'] in target_epoch_times, api_records))
        trade_logs_model_dataset = self._set_trade_logs_model_dataset(target_trade_logs_record)
        return self._trade_logs.create_data(trade_logs_model_dataset)

    def get_trade_logs_record(self, start_time, end_time):
        query_ = self._trade_logs.get_query(end_time, start_time, False)
        return self._trade_logs.get_record(query_)

    def _get_target_epoch_times(self, start_time, end_time):
        query_ = self._trade_logs.get_query(end_time, start_time, True)
        trade_logs_record = self._trade_logs.get_record(query_)
        return self._check_missing_records(
            trade_logs_record, start_time, end_time, self._period)

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

    def _get_ohlc_data_from_server(self, end_time):
        public_api = ZaifPublicApi()
        api_params = {'period': self._period, 'count': LIMIT_COUNT, 'to_epoch_time': end_time + 1}
        api_record = public_api.everything('ohlc_data', self._currency_pair, api_params)
        required_count = self._count + self._length
        if required_count <= LIMIT_COUNT:
            return api_record
        count = required_count - LIMIT_COUNT
        second_end_time = end_time - (LIMIT_COUNT * PERIOD_SECS[self._period]) + 1
        second_api_params =\
            {'period': self._period, 'count': count, 'to_epoch_time': second_end_time}
        second_api_record =\
            public_api.everything('ohlc_data', self._currency_pair, second_api_params)
        api_record = second_api_record + api_record
        return api_record


class MovingAverageManager:
    def __init__(self, currency_pair, period, count, length):
        self._currency_pair = currency_pair
        self._period = period
        self._count = count
        self._length = length
        self._moving_average = MovingAverageDao(self._currency_pair, self._period, self._length)

    def setup(self, ma_start_time, tl_start_time, end_time):
        moving_average_model_dataset = set()
        target_epoch_times = self._get_target_epoch_times(ma_start_time, end_time)
        if len(target_epoch_times) == 0:
            return
        trade_logs_moving_average =\
            self._moving_average.get_trade_logs_moving_average(end_time, tl_start_time)
        for i in self._get_moving_average(trade_logs_moving_average, target_epoch_times):
            moving_average_model_dataset.add(self._get_moving_average_model_dataset(i['time'],
                                                                                    i['sma'],
                                                                                    i['ema']))
        if self._moving_average.create_data(moving_average_model_dataset) is False:
            return False
        return self._moving_average.get_record(end_time, ma_start_time)

    def _get_target_epoch_times(self, start_time, end_time):
        moving_average_record = self._moving_average.get_record(end_time, start_time)
        return self._check_missing_records(
            moving_average_record, start_time, end_time, self._period)

    def _check_missing_records(self, moving_average_record, start_time, end_time, period):
        to_epoch_times = set([x.time for x in moving_average_record])
        target_epoch_times = set()
        for need_epoch_time in TradeLogsManager._get_need_epoch_times(start_time, end_time, period):
            if need_epoch_time not in to_epoch_times:
                target_epoch_times.add(need_epoch_time)
        return target_epoch_times

    def _get_moving_average(self, trade_logs_moving_average, target_epoch_times):
        for i in range(self._length, len(trade_logs_moving_average)):
            if trade_logs_moving_average[i].TradeLogs.time in target_epoch_times\
               or trade_logs_moving_average[i].TradeLogs.closed == 0:
                nums = self._get_nums(trade_logs_moving_average, i)
                sma = self._get_sma(nums)
                ema = self._get_ema(trade_logs_moving_average[i - 1], nums)
                yield {'time': trade_logs_moving_average[i].TradeLogs.time, 'sma': sma, 'ema': ema}

    def _get_nums(self, trade_logs_moving_average, i):
        nums = []
        for j in range(0, self._length):
            nums.append(trade_logs_moving_average[i - j].TradeLogs.time)
        return nums

    def _get_ema(self, last_trade_logs_moving_average, nums):
        current_price = nums.pop()
        if last_trade_logs_moving_average.MovingAverage is not None:
            last_ema = last_trade_logs_moving_average.MovingAverage.ema
        else:
            last_ema = np.average(nums)
        k = 2 / (self._length + 1)
        return (current_price * k + last_ema * (1 - k))

    def _get_sma(self, nums):
        nums.pop(0)
        return np.average(nums)

    def _get_moving_average_model_dataset(self, time_, sma_, ema_):
        return self._moving_average.model(
            time=time_,
            currency_pair=self._currency_pair,
            period=self._period,
            length=self._length,
            sma=sma_,
            ema=ema_)
    '''
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
