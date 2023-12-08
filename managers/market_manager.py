import numpy as np
import pandas as pd


# 市場データの管理
class MarketManager:
    def __init__(self, market_timeseries):
        # self.market_timeseries = np.load(market_timeseries)
        timeseries = pd.read_csv(market_timeseries)
        timeseries.columns = ['open', 'high', 'low', 'close', 'volume']
        self.market_timeseries = timeseries
        
        self.current_ohlcv = None
        self.future_ohlcv = None

        self.clock = clock

    def update_market_data(self):
        self.clock += 1
        if self.clock >= len(self.market_timeseries):
            raise Exception('Market data exhausted')
            
        self.current_ohlcv = self.market_timeseries.iloc[self.clock]
        self.future_ohlcv = self.market_timeseries.iloc[self.clock+1:self.clock+6]
    
    def get_price(self):
        current_price = self.current_ohlcv['close']
        return current_price
    
    def get_ohlcv(self):
        return self.current_ohlcv

    def get_future_ohlcv(self):
        return self.future_ohlcv