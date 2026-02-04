"""
Data Loading and Preprocessing Module
Handles multi-source OHLCV data loading with timeframe resampling and anti-leakage measures
"""

import pandas as pd
import numpy as np
from pathlib import Path
from typing import Dict, List, Tuple, Optional
import logging
from datetime import datetime, timedelta
import warnings
from sklearn.preprocessing import StandardScaler
import pickle

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DataLoader:
    """
    Loads OHLCV data from multiple sources:
    - CSV files (US stocks, ETFs, Indian stocks)
    - TXT files (US stocks)
    - Preprocesses with standardization and validation
    """
    
    def __init__(self, data_root: str = "datasets"):
        self.data_root = Path(data_root)
        self.scaler = StandardScaler()
        self.symbol_cache = {}
        
    def load_csv(self, file_path: str) -> Optional[pd.DataFrame]:
        """Load CSV with automatic header detection"""
        try:
            df = pd.read_csv(file_path)
            
            # Detect and standardize columns
            columns_map = {
                'date': 'Date', 'time': 'Time',
                'open': 'Open', 'high': 'High', 'low': 'Low', 'close': 'Close',
                'volume': 'Volume', 'symbol': 'Symbol',
                'prev close': 'Prev Close', 'last': 'Last', 'vwap': 'VWAP'
            }
            
            df.columns = [columns_map.get(c.lower().strip(), c) for c in df.columns]
            
            # Parse dates
            date_col = next((c for c in ['Date', 'date'] if c in df.columns), None)
            if date_col:
                df[date_col] = pd.to_datetime(df[date_col], errors='coerce')
                df = df.dropna(subset=[date_col])
                df = df.sort_values(date_col)
            
            # Select OHLCV
            ohlcv_cols = [c for c in ['Open', 'High', 'Low', 'Close', 'Volume'] 
                         if c in df.columns]
            if len(ohlcv_cols) >= 4:  # At least OHLC
                df = df[ohlcv_cols + [date_col]] if date_col else df[ohlcv_cols]
                df = df.dropna(subset=ohlcv_cols)
                return df
                
            return None
        except Exception as e:
            logger.warning(f"Failed to load {file_path}: {e}")
            return None
    
    def load_txt(self, file_path: str) -> Optional[pd.DataFrame]:
        """Load TXT format (US stocks)"""
        try:
            df = pd.read_csv(file_path, sep='\s+|,', engine='python')
            return self.load_csv(str(file_path))  # Reparse as CSV
        except Exception as e:
            logger.warning(f"Failed to load TXT {file_path}: {e}")
            return None
    
    def load_all_symbols(self, market: str = "all") -> Dict[str, pd.DataFrame]:
        """
        Load all available symbols from dataset folders
        Markets: 'US', 'NSE', 'BSE', 'CRYPTO', 'ETF', 'all'
        """
        data = {}
        
        market_folders = {
            'US': self.data_root / 'Stocks',
            'ETF': self.data_root / 'ETFs',
            'NSE': self.data_root / 'INDEX',  # And SCRIP
            'CRYPTO': self.data_root,  # BTCUSDT files at root
        }
        
        folders_to_scan = []
        if market == "all":
            folders_to_scan = list(market_folders.values())
        elif market in market_folders:
            folders_to_scan = [market_folders[market]]
        
        # Add SCRIP for NSE
        if market in ["NSE", "all"]:
            if (self.data_root / 'SCRIP').exists():
                folders_to_scan.append(self.data_root / 'SCRIP')
        
        for folder in folders_to_scan:
            if not folder.exists():
                continue
                
            for file in folder.glob('*'):
                if file.suffix in ['.csv', '.txt']:
                    symbol = file.stem.split('.')[0]
                    
                    if file.suffix == '.csv':
                        df = self.load_csv(str(file))
                    else:
                        df = self.load_txt(str(file))
                    
                    if df is not None and len(df) > 100:  # Minimum data points
                        data[symbol] = df
                        logger.info(f"Loaded {symbol}: {len(df)} records")
        
        # Also load root-level CSVs (AAPL, ADANIPORTS, BTCUSDT, etc.)
        for file in self.data_root.glob('*.csv'):
            if file.name not in ['NSE Symbols.CSV', 'FINAL_FROM_DF.csv']:
                symbol = file.stem
                df = self.load_csv(str(file))
                if df is not None and len(df) > 100:
                    data[symbol] = df
                    logger.info(f"Loaded {symbol}: {len(df)} records")
        
        logger.info(f"Total symbols loaded: {len(data)}")
        return data
    
    def resample_to_timeframe(self, df: pd.DataFrame, 
                             timeframe: str = '1h') -> pd.DataFrame:
        """
        Resample OHLCV to specified timeframe
        Supported: '5m', '15m', '1h', '4h', '1d', '1w', '1mo'
        Prevents forward-looking data (anti-leakage)
        """
        if 'Date' not in df.columns and 'date' not in df.columns:
            date_col = df.index.name or 'Date'
            df = df.reset_index()
        else:
            date_col = next((c for c in ['Date', 'date'] if c in df.columns))
        
        df = df.set_index(date_col)
        df.index = pd.to_datetime(df.index)
        
        # Resample: Close on close, OHLC aggregation
        resampled = pd.DataFrame()
        resampled['Open'] = df['Open'].resample(timeframe).first()
        resampled['High'] = df['High'].resample(timeframe).max()
        resampled['Low'] = df['Low'].resample(timeframe).min()
        resampled['Close'] = df['Close'].resample(timeframe).last()
        resampled['Volume'] = df['Volume'].resample(timeframe).sum()
        
        resampled = resampled.dropna()
        return resampled
    
    def split_train_test(self, df: pd.DataFrame, 
                        test_size: float = 0.2) -> Tuple[pd.DataFrame, pd.DataFrame]:
        """Time-aware train/test split (no shuffling for time series)"""
        split_idx = int(len(df) * (1 - test_size))
        return df.iloc[:split_idx], df.iloc[split_idx:]
    
    def normalize_ohlcv(self, df: pd.DataFrame, 
                       fit=True) -> pd.DataFrame:
        """
        Normalize OHLCV separately per symbol (prevent data leakage)
        Returns normalized values and stores scaler for inverse transform
        """
        if fit:
            normalized = self.scaler.fit_transform(df[['Open', 'High', 'Low', 'Close', 'Volume']])
        else:
            normalized = self.scaler.transform(df[['Open', 'High', 'Low', 'Close', 'Volume']])
        
        df_norm = df.copy()
        df_norm[['Open', 'High', 'Low', 'Close', 'Volume']] = normalized
        return df_norm
    
    def create_sequences(self, df: pd.DataFrame, 
                        lookback: int = 50,
                        lookahead: int = 5) -> Tuple[np.ndarray, np.ndarray]:
        """
        Create sequences for LSTM training
        lookback: historical bars
        lookahead: future bars to predict
        """
        X, y = [], []
        
        for i in range(lookback, len(df) - lookahead):
            # Input: last 'lookback' candles (OHLCV)
            X.append(df.iloc[i-lookback:i][['Open', 'High', 'Low', 'Close', 'Volume']].values)
            
            # Target: future close price direction (1=up, 0=down, 2=sideways)
            future_close = df.iloc[i+lookahead]['Close']
            current_close = df.iloc[i]['Close']
            change_pct = (future_close - current_close) / current_close
            
            if change_pct > 0.01:  # >1% up
                y.append(1)
            elif change_pct < -0.01:  # <-1% down
                y.append(0)
            else:
                y.append(2)  # Sideways
        
        return np.array(X), np.array(y)
    
    def save_cache(self, data: Dict, path: str = "ml_data_cache.pkl"):
        """Save loaded data for faster subsequent runs"""
        with open(path, 'wb') as f:
            pickle.dump(data, f)
        logger.info(f"Data cached to {path}")
    
    def load_cache(self, path: str = "ml_data_cache.pkl") -> Optional[Dict]:
        """Load cached data"""
        try:
            with open(path, 'rb') as f:
                return pickle.load(f)
        except:
            return None


class DataValidator:
    """Validates data quality and detects anomalies"""
    
    @staticmethod
    def check_gaps(df: pd.DataFrame, max_gap_days: int = 5) -> bool:
        """Check for excessive gaps in trading data"""
        if df.index.name is None or not isinstance(df.index, pd.DatetimeIndex):
            return True
        
        gaps = df.index.to_series().diff()
        large_gaps = gaps[gaps > timedelta(days=max_gap_days)]
        
        if len(large_gaps) > 0:
            logger.warning(f"Data has {len(large_gaps)} gaps > {max_gap_days} days")
            return False
        return True
    
    @staticmethod
    def check_outliers(df: pd.DataFrame, z_threshold: float = 4.0) -> int:
        """Detect price outliers using Z-score"""
        from scipy import stats
        z_scores = np.abs(stats.zscore(df['Close']))
        outliers = (z_scores > z_threshold).sum()
        if outliers > 0:
            logger.warning(f"Detected {outliers} price outliers")
        return outliers
    
    @staticmethod
    def check_stationarity(series: pd.Series) -> bool:
        """ADF test for stationarity"""
        from statsmodels.tsa.stattools import adfuller
        try:
            result = adfuller(series.dropna())
            is_stationary = result[1] < 0.05  # p-value < 5%
            if not is_stationary:
                logger.info(f"Series not stationary (p={result[1]:.4f})")
            return is_stationary
        except:
            return True


if __name__ == "__main__":
    # Example usage
    loader = DataLoader()
    
    # Load all US stocks
    us_data = loader.load_all_symbols("US")
    print(f"Loaded {len(us_data)} US symbols")
    
    # Load NSE stocks
    nse_data = loader.load_all_symbols("NSE")
    print(f"Loaded {len(nse_data)} NSE symbols")
    
    # Example: Prepare AAPL for training
    if 'AAPL' in us_data:
        df = us_data['AAPL']
        df_daily = loader.resample_to_timeframe(df, '1d')
        train_df, test_df = loader.split_train_test(df_daily, test_size=0.2)
        print(f"AAPL: {len(train_df)} train, {len(test_df)} test")
