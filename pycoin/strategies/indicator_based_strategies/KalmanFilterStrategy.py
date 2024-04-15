from datetime import datetime
from pycoin import Utils
from .._strategy_BASE import _StrategyBASE
from pykalman import KalmanFilter
import pandas as pd
import numpy as np


class Kalmanfilter(_StrategyBASE):
    def __init__(self, symbol: str, timeframe: str, data_exchange: str = "binance", 
                 start_time: datetime | None | int = None,
                 dataName_format: str = "{symbol}|{exchange}|{timeframe}",
                 observation_covariance=0.05, transition_covariance=0.01, **kwargs) -> None:
        
        super().__init__(symbol, timeframe, data_exchange, start_time, dataName_format, **kwargs)
        self.kalman_kwargs = {"n_dim_obs":1, "n_dim_state":1,
                              "observation_covariance":observation_covariance,
                              "transition_covariance":transition_covariance}
        
    def filter(self, series):
        kf = KalmanFilter(initial_state_mean=series.iloc[0], **self.kalman_kwargs)
        state_means, state_covariances = kf.filter(series.values)
        self.filtered_data = pd.Series(state_means.flatten(), index=series.index)
        return self.filtered_data
    
    def find_pos_byHighLows(self, dataframe:pd.DataFrame = pd.DataFrame(), **kwargs):
        if dataframe.empty: 
            assert kwargs.get("init_update", True), "no data available"
            self.update_data
            df = self.df.copy()
        else:
            df = dataframe.copy()
        
        df["Kalman"] = self.filtered_data
        high_idx, low_idx = Utils.get_signal_HighsLows_ind(self.filtered_data.values, **kwargs )
        lows_df, highs_df = df.iloc[low_idx], df.iloc[high_idx]
        df["Position_side"] = 0
        df.loc[highs_df.index, "Position_side"] = 1
        df.loc[lows_df.index, "Position_side"] = -1
        if kwargs.get("inplace", True): 
            self.df = df
            self.df.Name = getattr(self.df, "Name", "")
        return df

    
    def plot(self, **kwargs):
        fig = super().plot(**kwargs)
        fig.add_scatter(x = self.df.index, y = self.df["Kalman"],  
                        line_shape='spline', line={"color":kwargs.get("color", "black")},
                        name = "Kalman")
        for side, grp_df in self.df.groupby("Position_side"):
            if side == 0: continue
            for ind, row in grp_df.iterrows():
                self.plotter.draw_circle(fig, [ind, row["Kalman"]], 
                                         fillcolor = "blue" if side == 1 else "yellow", 
                                         R = kwargs.get('R', 100), 
                                         y_scale=kwargs.get("y_scale", 1))
        return fig
        
    

class KalmanfilterDeploy:
    def __init__(self, observation_covariance=0.05,
                 transition_covariance=0.01, **kwargs) -> None:
    
        self.kalman_kwargs = {"n_dim_obs":1, "n_dim_state":1,
                                "observation_covariance":observation_covariance,
                                "transition_covariance":transition_covariance}
    
    def filter(self, series):
        kf = KalmanFilter(initial_state_mean=series.iloc[0], **self.kalman_kwargs)
        state_means, state_covariances = kf.filter(series.values)
        self.filtered_data = pd.Series(state_means.flatten(), index=series.index)
        return self.filtered_data


    def generate_signal(self, dataframe:pd.DataFrame,
                        filter_column:str = "Close", dist_pct: float = 0.01 ,
                        **kwargs):
        """generates LONG, SHORT signal by finding high and lows and make order in 
        those price. adds "Position_side", "Kalman", "upper_limit", "lower_limit" columns

        Args:
            dataframe (pd.DataFrame)
            filter_column (str, optional)
            dist_pct (float, optional): distance from column price to find price range. Defaults to 0.01.

        Returns:
            pd.Dataframe
        """        
        df = dataframe.copy()
        df["Kalman"] = self.filter(df[filter_column])
        high_idx, low_idx = Utils.get_signal_HighsLows_ind(df["Kalman"].values, **kwargs )
        lows_df, highs_df = df.iloc[low_idx], df.iloc[high_idx]
        df["Position_side"] = 0
        df.loc[highs_df.index, "Position_side"] = 1
        df.loc[lows_df.index, "Position_side"] = -1
        df = self.generate_position_price_range(df, filter_column, dist_pct)
        if kwargs.get("inplace", True): self.df = df
        return df
    
    
    def generate_position_price_range(self, dataframe: pd.DataFrame, 
                                      column:str = "Close", dist_pct: float = 0.01):
        """evaluates range of price than a position can be excuted if 
        there is a signal

        Args:
            dataframe (pd.DataFrame)
            column (str, optional): column to evalute the range from. Defaults to "Close".
            dist_pct (float, optional): acceptable distance from price in pct. Defaults to 0.01.

        Returns:
            pd.DataFrame: df consisting "upper_limit" and "lower_limit" column
        """        
        upper_limit = np.where(dataframe["Position_side"] != 0, 
                               dataframe[column]+dist_pct*dataframe[column], 0)
        
        lower_limit = np.where(dataframe["Position_side"]!=0,
                               dataframe[column]-dist_pct*dataframe[column], 0)
        c1 = ((dataframe[column] <= upper_limit) & (dataframe[column] >= lower_limit))
        c3 = ((upper_limit!=0) & (lower_limit!=0)) 
        dataframe["IsInPriceRange"] = c1 & c3
        return dataframe
