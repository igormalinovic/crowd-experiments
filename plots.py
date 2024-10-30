import pandas as pd
import plotly.graph_objects as go

from plotly.subplots import make_subplots

from market_data import MarketData
from signals import Signals
from util import AssetType, Interval

class Plots:
    def __init__(self, bench_assets: list[str]) -> None:
        self.data_service = MarketData()
        self.signal_service = Signals()
        self.bench_assets = bench_assets

    def get(
        self,
        market_prefix: str,
        asset_type: AssetType,
        signal_prefix: str,
        interval: Interval,
    ) -> list[go.Figure]:
        market_df = self.data_service.get(market_prefix, asset_type, interval)
        signal_df = self.signal_service.compute(signal_prefix, market_df, interval)
        plot_df = self.get_plot_df(market_df, signal_df)
        return [self.get_figure(plot_df, asset) for asset in self.bench_assets]
    
    def get_plot_df(self, market_df: pd.DataFrame, signal_df: pd.DataFrame) -> pd.DataFrame:
        asset_dfs = [
            self.data_service.format_asset_series(
                market_df, asset, field='close') for asset in self.bench_assets   
        ]
        df = pd.concat(objs=[signal_df.set_index('time')]+asset_dfs, axis=1)
        df.index = pd.to_datetime(df.index, unit='s', utc=True)
        return df

    def get_figure(self, plot_df: pd.DataFrame, asset: str) -> go.Figure:
        return make_subplots(specs=[[{"secondary_y": True}]]) \
            .add_trace(
                go.Scatter(x=plot_df.index, y=plot_df['signal'], name="Signal"),
                secondary_y=False,
            ) \
            .add_trace(
                go.Scatter(x=plot_df.index, y=plot_df[asset], name=asset),
                secondary_y=True,
            ) \
            .update_layout(title_text=f"Signal vs. {asset}") \
            .update_xaxes(title_text="Time") \
            .update_yaxes(title_text="<b>Signal</b>", secondary_y=False) \
            .update_yaxes(title_text=f"<b>{asset}</b>", secondary_y=True)
    