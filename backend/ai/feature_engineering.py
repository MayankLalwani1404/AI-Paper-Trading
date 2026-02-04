"""
Feature Engineering Module
Comprehensive TA indicators, candlestick patterns, and advanced features
with anti-leakage and forward-fill prevention
"""

import pandas as pd
import numpy as np
import ta
from typing import Dict, List, Tuple, Optional
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class TechnicalIndicators:
    """Calculate technical indicators without lookahead bias"""
    
    @staticmethod
    def rsi(df: pd.DataFrame, period: int = 14, column: str = 'Close') -> pd.Series:
        """RSI - prevents lookahead by calculating only from available data"""
        return ta.momentum.RSIIndicator(close=df[column], window=period).rsi()
    
    @staticmethod
    def macd(df: pd.DataFrame, 
             fast: int = 12, slow: int = 26, signal: int = 9) -> Tuple[pd.Series, pd.Series, pd.Series]:
        """MACD (Moving Average Convergence Divergence)"""
        macd_obj = ta.trend.MACD(close=df['Close'], window_fast=fast, window_slow=slow, window_sign=signal)
        return macd_obj.macd(), macd_obj.macd_signal(), macd_obj.macd_diff()
    
    @staticmethod
    def moving_averages(df: pd.DataFrame, periods: List[int] = [20, 50, 200]) -> Dict[str, pd.Series]:
        """Simple and Exponential Moving Averages"""
        mas = {}
        for p in periods:
            mas[f'SMA_{p}'] = df['Close'].rolling(window=p).mean()
            mas[f'EMA_{p}'] = df['Close'].ewm(span=p, adjust=False).mean()
        return mas
    
    @staticmethod
    def bollinger_bands(df: pd.DataFrame, period: int = 20, std_dev: int = 2) -> Tuple[pd.Series, pd.Series, pd.Series]:
        """Bollinger Bands"""
        bb = ta.volatility.BollingerBands(close=df['Close'], window=period, window_dev=std_dev)
        return bb.bollinger_hband(), bb.bollinger_mavg(), bb.bollinger_lband()
    
    @staticmethod
    def atr(df: pd.DataFrame, period: int = 14) -> pd.Series:
        """Average True Range (volatility)"""
        return ta.volatility.AverageTrueRange(high=df['High'], low=df['Low'], close=df['Close'], 
                                             window=period).average_true_range()
    
    @staticmethod
    def volume_sma(df: pd.DataFrame, period: int = 20) -> pd.Series:
        """Volume Moving Average"""
        return df['Volume'].rolling(window=period).mean()
    
    @staticmethod
    def volume_oscillator(df: pd.DataFrame, fast: int = 12, slow: int = 26) -> pd.Series:
        """Volume Oscillator = (Fast EMA - Slow EMA) of Volume"""
        fast_vol = df['Volume'].ewm(span=fast, adjust=False).mean()
        slow_vol = df['Volume'].ewm(span=slow, adjust=False).mean()
        return (fast_vol - slow_vol) / slow_vol
    
    @staticmethod
    def on_balance_volume(df: pd.DataFrame) -> pd.Series:
        """On Balance Volume"""
        return ta.volume.OnBalanceVolumeIndicator(close=df['Close'], volume=df['Volume']).on_balance_volume()
    
    @staticmethod
    def price_volume_trend(df: pd.DataFrame) -> pd.Series:
        """Price Volume Trend"""
        return ta.volume.VolumePriceTrendIndicator(close=df['Close'], volume=df['Volume']).volume_price_trend()
    
    @staticmethod
    def stochastic(df: pd.DataFrame, k_period: int = 14, d_period: int = 3) -> Tuple[pd.Series, pd.Series]:
        """Stochastic Oscillator"""
        stoch = ta.momentum.StochasticOscillator(high=df['High'], low=df['Low'], close=df['Close'],
                                               window=k_period, smooth_window=d_period)
        return stoch.stoch(), stoch.stoch_signal()
    
    @staticmethod
    def adx(df: pd.DataFrame, period: int = 14) -> pd.Series:
        """Average Directional Index (trend strength)"""
        return ta.trend.ADXIndicator(high=df['High'], low=df['Low'], close=df['Close'], 
                                    window=period).adx()
    
    @staticmethod
    def vortex(df: pd.DataFrame, period: int = 14) -> Tuple[pd.Series, pd.Series]:
        """Vortex Indicator"""
        vi = ta.trend.VortexIndicator(high=df['High'], low=df['Low'], close=df['Close'], window=period)
        pos_fn = getattr(vi, "vortex_indicator_pos", None) or getattr(vi, "vortex_indicator_positive")
        neg_fn = getattr(vi, "vortex_indicator_neg", None) or getattr(vi, "vortex_indicator_negative")
        return pos_fn(), neg_fn()


class CandlestickPatterns:
    """Candlestick pattern recognition (rule-based)"""
    
    @staticmethod
    def is_bullish_engulfing(df: pd.DataFrame, idx: int) -> bool:
        """Previous bar is bearish, current bar opens below and closes above previous"""
        if idx < 1:
            return False
        
        prev_body = abs(df.iloc[idx-1]['Close'] - df.iloc[idx-1]['Open'])
        curr_body = abs(df.iloc[idx]['Close'] - df.iloc[idx]['Open'])
        
        prev_bearish = df.iloc[idx-1]['Close'] < df.iloc[idx-1]['Open']
        curr_bullish = df.iloc[idx]['Close'] > df.iloc[idx]['Open']
        
        engulfs = (df.iloc[idx]['Open'] < df.iloc[idx-1]['Close'] and 
                  df.iloc[idx]['Close'] > df.iloc[idx-1]['Open'])
        
        return prev_bearish and curr_bullish and engulfs and curr_body > prev_body * 0.5
    
    @staticmethod
    def is_hammer(df: pd.DataFrame, idx: int) -> bool:
        """Small body, long lower wick, minimal upper wick"""
        if idx < 1:
            return False
        
        open_, close, high, low = df.iloc[idx][['Open', 'Close', 'High', 'Low']]
        
        body = abs(close - open_)
        lower_wick = min(open_, close) - low
        upper_wick = high - max(open_, close)
        total_range = high - low
        
        return (lower_wick > body * 2 and upper_wick < body * 0.5 and 
               body > total_range * 0.1 and close > open_)  # Bullish hammer
    
    @staticmethod
    def is_doji(df: pd.DataFrame, idx: int, threshold: float = 0.1) -> bool:
        """Open and close are very close"""
        open_, close = df.iloc[idx][['Open', 'Close']]
        return abs(open_ - close) / open_ < threshold
    
    @staticmethod
    def is_morning_star(df: pd.DataFrame, idx: int) -> bool:
        """3-bar pattern: down day, short-body day, up day"""
        if idx < 2:
            return False
        
        # Day 1: bearish
        day1_bearish = df.iloc[idx-2]['Close'] < df.iloc[idx-2]['Open']
        
        # Day 2: small body, gap down
        day2_body = abs(df.iloc[idx-1]['Close'] - df.iloc[idx-1]['Open'])
        day2_small = day2_body < (df.iloc[idx-2]['Open'] - df.iloc[idx-2]['Close']) * 0.5
        
        # Day 3: bullish, closes into day 1 body
        day3_bullish = df.iloc[idx]['Close'] > df.iloc[idx]['Open']
        day3_strong = df.iloc[idx]['Close'] > ((df.iloc[idx-2]['Open'] + df.iloc[idx-2]['Close']) / 2)
        
        return day1_bearish and day2_small and day3_bullish and day3_strong
    
    @staticmethod
    def detect_all_patterns(df: pd.DataFrame, idx: int) -> Dict[str, bool]:
        """Detect all patterns at given index"""
        return {
            'bullish_engulfing': CandlestickPatterns.is_bullish_engulfing(df, idx),
            'hammer': CandlestickPatterns.is_hammer(df, idx),
            'doji': CandlestickPatterns.is_doji(df, idx),
            'morning_star': CandlestickPatterns.is_morning_star(df, idx),
        }


class FeatureEngineer:
    """Main feature engineering orchestrator"""
    
    def __init__(self, lookback: int = 50):
        self.lookback = lookback
        self.ti = TechnicalIndicators()
        self.cp = CandlestickPatterns()
    
    def create_features(self, df: pd.DataFrame, 
                       include_patterns: bool = True) -> pd.DataFrame:
        """
        Create comprehensive feature set
        NO LOOKAHEAD BIAS: All indicators calculated from historical data only
        """
        features = df.copy()
        
        # === Momentum ===
        features['RSI_14'] = self.ti.rsi(df, period=14)
        features['RSI_7'] = self.ti.rsi(df, period=7)
        
        # === Trend ===
        macd, macd_signal, macd_diff = self.ti.macd(df)
        features['MACD'] = macd
        features['MACD_Signal'] = macd_signal
        features['MACD_Hist'] = macd_diff
        
        mas = self.ti.moving_averages(df, [10, 20, 50, 200])
        for name, series in mas.items():
            features[name] = series
        
        # === Volatility ===
        features['ATR_14'] = self.ti.atr(df, period=14)
        
        bb_upper, bb_mid, bb_lower = self.ti.bollinger_bands(df, period=20)
        features['BB_Upper'] = bb_upper
        features['BB_Mid'] = bb_mid
        features['BB_Lower'] = bb_lower
        
        # === Volume ===
        features['Volume_SMA_20'] = self.ti.volume_sma(df, period=20)
        features['Volume_Oscillator'] = self.ti.volume_oscillator(df)
        features['OBV'] = self.ti.on_balance_volume(df)
        
        # === Oscillators ===
        stoch_k, stoch_d = self.ti.stochastic(df)
        features['Stochastic_K'] = stoch_k
        features['Stochastic_D'] = stoch_d
        
        vi_pos, vi_neg = self.ti.vortex(df)
        features['VI_Pos'] = vi_pos
        features['VI_Neg'] = vi_neg
        
        features['ADX_14'] = self.ti.adx(df, period=14)
        
        # === Price Action ===
        features['Daily_Return'] = df['Close'].pct_change()
        features['Price_Range_Pct'] = (df['High'] - df['Low']) / df['Open']
        features['Body_Range_Pct'] = (df['Close'] - df['Open']) / df['Open']
        features['Upper_Wick_Pct'] = (df['High'] - df[['Open', 'Close']].max(axis=1)) / df['Open']
        features['Lower_Wick_Pct'] = (df[['Open', 'Close']].min(axis=1) - df['Low']) / df['Open']
        
        # === Volume Profile ===
        features['Volume_vs_MA'] = df['Volume'] / features['Volume_SMA_20']
        features['Volume_Trend'] = df['Volume'].rolling(window=5).mean() / features['Volume_SMA_20']
        
        # === Candlestick Patterns (as binary features) ===
        if include_patterns:
            for pattern in ['bullish_engulfing', 'hammer', 'doji', 'morning_star']:
                features[f'Pattern_{pattern}'] = 0
            
            for idx in range(self.lookback, len(df)):
                patterns = self.cp.detect_all_patterns(df, idx)
                for pattern, is_present in patterns.items():
                    if is_present:
                        features.loc[features.index[idx], f'Pattern_{pattern}'] = 1
        
        # === Price Position Relative to Key Levels ===
        features['Price_vs_SMA50'] = (features['Close'] - features['SMA_50']) / features['SMA_50']
        features['Price_vs_SMA200'] = (features['Close'] - features['SMA_200']) / features['SMA_200']
        features['Price_vs_BB'] = (features['Close'] - features['BB_Lower']) / \
                                 (features['BB_Upper'] - features['BB_Lower'])
        
        # === Cross-over signals (lag-free) ===
        features['SMA20_vs_SMA50'] = np.where(features['SMA_20'] > features['SMA_50'], 1, 0)
        features['SMA50_vs_SMA200'] = np.where(features['SMA_50'] > features['SMA_200'], 1, 0)
        features['EMA10_vs_EMA20'] = np.where(features['EMA_10'] > features['EMA_20'], 1, 0)
        
        # Drop NaN rows created by indicators
        features = features.dropna()
        
        return features
    
    def get_feature_importance_names(self) -> List[str]:
        """Get list of feature names for model training"""
        return [
            # Momentum
            'RSI_14', 'RSI_7',
            # Trend
            'MACD', 'MACD_Signal', 'MACD_Hist',
            'SMA_10', 'SMA_20', 'SMA_50', 'SMA_200',
            'EMA_10', 'EMA_20', 'EMA_50', 'EMA_200',
            # Volatility
            'ATR_14', 'BB_Upper', 'BB_Mid', 'BB_Lower',
            # Volume
            'Volume_SMA_20', 'Volume_Oscillator', 'OBV',
            # Oscillators
            'Stochastic_K', 'Stochastic_D', 'VI_Pos', 'VI_Neg', 'ADX_14',
            # Price Action
            'Daily_Return', 'Price_Range_Pct', 'Body_Range_Pct',
            'Upper_Wick_Pct', 'Lower_Wick_Pct',
            # Volume Profile
            'Volume_vs_MA', 'Volume_Trend',
            # Relative Positioning
            'Price_vs_SMA50', 'Price_vs_SMA200', 'Price_vs_BB',
            'SMA20_vs_SMA50', 'SMA50_vs_SMA200', 'EMA10_vs_EMA20',
        ]


if __name__ == "__main__":
    from backend.ai.data_loader import DataLoader
    
    # Example
    loader = DataLoader()
    us_data = loader.load_all_symbols("US")
    
    if 'AAPL' in us_data:
        df = us_data['AAPL']
        df_daily = loader.resample_to_timeframe(df, '1d')
        
        engineer = FeatureEngineer(lookback=50)
        features = engineer.create_features(df_daily)
        
        print(f"Created {features.shape[1]} features")
        print(features.head())
        print("\nFeature names:")
        print(engineer.get_feature_importance_names())
