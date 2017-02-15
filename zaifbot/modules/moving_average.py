from zaifapi import ZaifPublicApi
from zaifbot.bot_common.bot_const import PERIOD_SECS, LIMIT_COUNT
from zaifbot.modules.dao.moving_average import TradeLogsDao, MovingAverageDao


class TradeLogsManager:
    def __init__(self, currency_pair, period):
        self._currency_pair = currency_pair
        self._period = period
        self._trade_logs = TradeLogsDao(self._currency_pair, self._period)

    def setup(self, start_epoch_time, end_epoch_time):
        target_epoch_times = self._get_target_epoch_times(start_epoch_time, end_epoch_time)
        if len(target_epoch_times) == 0:
            return
        api_records = self._get_ohlc_data_from_server(end_epoch_time)
        target_trade_logs_record = list(filter(lambda x: x['time'] in target_epoch_times, api_records))
        trade_logs_model_dataset = self._set_trade_logs_model_dataset(target_trade_logs_record)
        self._trade_logs.create_data(trade_logs_model_dataset)

    def get_trade_logs_record(self, start_epoch_time, end_epoch_time):
        return self._trade_logs.get_record(end_epoch_time, start_epoch_time)

    def _get_target_epoch_times(self, start_epoch_time, end_epoch_time):
        trade_logs_record = self._trade_logs.get_record(end_epoch_time, start_epoch_time)
        return self._check_missing_records(trade_logs_record, start_epoch_time, end_epoch_time, self._period)

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
                closed=trade_logs['closed']
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
        api_params = {'period': self._period, 'count': LIMIT_COUNT, 'to_epoch_time': end_epoch_time}
        return public_api.everything('ohlc_data', self._currency_pair, api_params)


class MovingAverageManager:
    def __init__(self, currency_pair, period, length):
        self._currency_pair = currency_pair
        self._period = period
        self._length = length
        self._moving_average = MovingAverageDao(self._currency_pair, self._period, self._length)

    def setup(self, start_epoch_time, end_epoch_time):
        target_epoch_times = self._get_target_epoch_times(start_epoch_time, end_epoch_time)
        if len(target_epoch_times) == 0:
            return
        trade_logs = TradeLogsManager(self._currency_pair, self._period)
        trade_logs_record = trade_logs.get_trade_logs_record(start_epoch_time, end_epoch_time)
        target_trade_logs_record = list(filter(lambda x: x.time in target_epoch_times, trade_logs_record))
        moving_average = self._get_moving_average(target_trade_logs_record)
        #moving_average_model_dataset = self._set_moving_average_model_dataset(moving_average)
        #self._moving_average.create_data(moving_average_model_dataset)

    def _get_target_epoch_times(self, start_epoch_time, end_epoch_time):
        moving_average_record = self._moving_average.get_record(end_epoch_time, start_epoch_time)
        return self._check_missing_records(moving_average_record, start_epoch_time, end_epoch_time, self._period)

    def _check_missing_records(self, moving_average_record, start_time, end_time, period):
        to_epoch_times = set([x.time for x in moving_average_record])
        target_epoch_times = set()
        for need_epoch_time in TradeLogsManager._get_need_epoch_times(start_time, end_time, period):
            if need_epoch_time not in to_epoch_times:
                target_epoch_times.add(need_epoch_time)
        return target_epoch_times

    def _get_moving_average(self, target_trade_logs_record):
        #　ここにsma/ema算出処理を書く


