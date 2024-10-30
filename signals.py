import numpy as np
import pandas as pd

from numpy.typing import NDArray
from constants import (
    DEFAULT_CORRELATION_WINDOW, DEFAULT_DATA_PATH, DEFAULT_DIGITAL_ASSETS, 
    DEFAULT_DISCRETIZATION_THRESHOLD, DEFAULT_GAP_THRESHOLD, DEFAULT_SMOOTHING_WINDOW
)
from util import Interval, get_last_complete_period

class Signals:
    def __init__(
        self,
        data_path=DEFAULT_DATA_PATH,
        assets=DEFAULT_DIGITAL_ASSETS,
        corr_win=DEFAULT_CORRELATION_WINDOW,
        smth_win=DEFAULT_SMOOTHING_WINDOW,
        dis_thr=DEFAULT_DISCRETIZATION_THRESHOLD,
        gap_thr=DEFAULT_GAP_THRESHOLD
    ) -> None:
        self.data_path = data_path
        self.assets = assets
        self.corr_win = corr_win
        self.smth_win = smth_win
        self.dis_thr = dis_thr
        self.gap_thr = gap_thr

    def compute(self, file_prefix: str, df: pd.DataFrame, interval: Interval) -> pd.DataFrame:
        try:
            signal_df = self.update(file_prefix, df, interval)
            return signal_df
        except FileNotFoundError:
            print('Market signals are getting computed.')
            times=sorted(df['time'].unique())
            signal_df = self.compute_signal_df(df, times, interval)
            signal_df.to_csv(self.format_path(file_prefix, interval), index=False)
            print('Computation completed.')
            return signal_df
    
    def update(self, file_prefix: str, df: pd.DataFrame, interval: Interval) -> pd.DataFrame:
        file_path = self.format_path(file_prefix, interval)
        last_signal_df = pd.read_csv(file_path)
        last_complete_period = get_last_complete_period(interval)
        since = last_signal_df['time'].iloc[-1]
        if since < last_complete_period:
            print('Signal data is getting updated.')
            step = interval.value * 60
            df = df.loc[df['time'] > since - (self.corr_win + self.smth_win) * step]
            times = range(since+step, last_complete_period+step, step)
            signal_df = self.compute_signal_df(df, times, interval)
            signal_df.to_csv(file_path, header=False, index=False, mode='a')
            print('Update complete.')
        else:
            print('Signal data is up to date.')
        return pd.read_csv(file_path)
    
    def compute_signal_df(self, df: pd.DataFrame, times: list[int], interval: Interval) -> pd.DataFrame:
        signal_data = [
            [
                end_time, 
                self.compute_window_signal(df, end_time, interval)
            ] for end_time in times
        ]
        return pd.DataFrame(data=signal_data, columns=['time', 'signal'])
    
    def compute_window_signal(self, df: pd.DataFrame, end_time: int, interval: Interval) -> int:
        win_df = self.get_window_df(df, end_time, interval)
        times = sorted(win_df['time'].unique(), reverse=True)
        if len(times) == self.corr_win + self.smth_win:
            # Each 'column' (i.e., secondary axis) of the matrix 'prices'
            # contains prices ordered decreasingly according to the timestamp
            prices = np.array([self.format_prices(win_df, time) for time in times])
            returns = self.get_returns(prices)
            return self.compute_dseg(returns)
    
    def get_window_df(self, df: pd.DataFrame, end_time: int, interval: Interval) -> pd.DataFrame:
        start_time = end_time - (self.corr_win + self.smth_win - 1) * interval.value * 60
        return df[['asset', 'time', 'close']] \
            .loc[(df['time'] >= start_time) & (df['time'] <= end_time)]
    
    def format_prices(self, df: pd.DataFrame, time: int) -> list[float]:
        time_df = df.loc[df['time'] == time][['asset', 'close']]
        asset_to_price = { row[1]: row[2] for row in time_df.itertuples() }
        return [asset_to_price.get(asset, np.nan) for asset in self.assets]
    
    def get_returns(self, prices: NDArray) -> NDArray:
        prices[np.isnan(prices)] = 1
        return (prices / np.roll(prices, -1, axis=0) - np.ones(prices.shape))[:-1,:]

    def compute_dseg(self, returns: NDArray) -> int:
        eigvals_per_win = np.array([
            self.get_eigvals(
                ret_window=returns[i:i+self.corr_win,:]
            ) for i in range(self.smth_win)
        ])
        mean_eigvals = np.mean(eigvals_per_win, axis=0)
        return self.get_eig_gap(eigvals=mean_eigvals)

    def get_eigvals(self, ret_window: NDArray) -> list[float]:
        # A warning can be caused by an asset with variance 0:
        corr_matrix = np.corrcoef(ret_window, rowvar=False)
        dis_matrix = self.discretize(corr_matrix)
        vals, _ = np.linalg.eigh(dis_matrix)
        # Order the eigen values by the magnitude
        return sorted(vals, key=abs, reverse=True)
    
    def discretize(self, matrix: NDArray) -> NDArray:
        matrix[np.isnan(matrix)] = 0
        matrix[matrix < self.dis_thr] = 0
        matrix[matrix >= self.dis_thr] = 1
        return matrix

    def get_eig_gap(self, eigvals: NDArray) -> int:
        return next(idx for idx, val in enumerate(eigvals) if abs(val) < self.gap_thr)
    
    def format_path(self, file_prefix: str, interval: Interval) -> str:
        return f'{self.data_path}/{file_prefix}_{interval.value}.csv'
