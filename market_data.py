import pandas as pd
import requests

from constants import (
    DEFAULT_DIGITAL_ASSETS, DEFAULT_FIAT,
    DIGITAL_ASSET_DATA_API, DEFAULT_DATA_PATH
)
from util import AssetType, Interval, get_last_complete_period

class MarketData:
    def __init__(
        self,
        data_path=DEFAULT_DATA_PATH,
        fiat=DEFAULT_FIAT,
        digital_assets=DEFAULT_DIGITAL_ASSETS,
        digital_asset_data_api=DIGITAL_ASSET_DATA_API
    ) -> None:
        self.data_path = data_path
        self.fiat = fiat
        self.digital_assets = digital_assets
        self.digital_asset_data_api = digital_asset_data_api

    def get(self, file_prefix: str, asset_type: AssetType, interval: Interval) -> pd.DataFrame:
        if asset_type == AssetType.DIGITAL:
            try:
                df = self.update(file_prefix, asset_type, interval)
                return df
            except FileNotFoundError:
                print('Market data is getting downloaded.')
                df = pd.concat([
                    self.get_digital_asset_data(asset, interval) for asset in self.digital_assets
                ])
                df.to_csv(self.format_path(file_prefix, interval), index=False)
                print('Download complete.')
                return df

    def update(self, file_prefix: str, asset_type: AssetType, interval: Interval) -> pd.DataFrame:
        if asset_type == AssetType.DIGITAL:
            file_path = self.format_path(file_prefix, interval)
            df = pd.read_csv(file_path)
            last_complete_period = get_last_complete_period(interval)
            since = df['time'].iloc[-1]
            if since < last_complete_period:
                print('Market data is getting updated.') 
                df = pd.concat([
                    self.get_digital_asset_data(asset, interval, since) for asset in self.digital_assets
                ])
                df.to_csv(file_path, header=False, index=False, mode='a')
                print('Update complete.')
            else:
                print('Market data is up to date.')
            return pd.read_csv(file_path)

    def get_digital_asset_data(self, asset: str, interval: Interval, since: int = None) -> pd.DataFrame:
        url = f'{self.digital_asset_data_api}?pair={asset}{self.fiat}&interval={interval.value}'
        if since is not None:
            url += f'&since={since}'
        result = requests.get(url).json()['result']
        values = next(iter(result.values()))
        return self.format_digital_asset_data(asset=asset, data=values[:-1])
    
    def format_digital_asset_data(self, asset: str, data: list[list[int,str]]) -> pd.DataFrame:
        float_columns = ['open', 'high', 'low', 'close', 'vwap', 'volume']
        columns = ['time'] + float_columns + ['count']
        df = pd.DataFrame(data=data, columns=columns)
        asset_column = 'asset'
        df[asset_column] = asset
        for column in float_columns:
            df[column] = df[column].astype('float')
        return df.reindex(columns=[asset_column]+columns)
    
    def format_path(self, file_prefix: str, interval: Interval) -> str:
        return f'{self.data_path}/{file_prefix}_{interval.value}.csv'
    
    def format_asset_series(self, market_df: pd.DataFrame, asset: str, field: str) -> pd.DataFrame:
        return market_df[['asset', 'time', field]] \
            .loc[market_df['asset'] ==  asset] \
            .drop(columns=['asset']) \
            .rename(columns={ field: asset }) \
            .set_index('time')
