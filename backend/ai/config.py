"""
ML Configuration and Constants
Centralized settings for all ML operations
"""

from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List


@dataclass
class MLConfig:
    """ML system configuration"""
    
    # Paths
    data_path: str = "datasets"
    model_path: str = "ml_models"
    
    # Data settings
    min_data_points: int = 200
    lookback_period: int = 50
    lookahead_period: int = 5
    
    # Ensemble weights (should sum to 1.0)
    ensemble_weights: Dict[str, float] = None
    
    # Training settings
    train_val_split: float = 0.8
    batch_size: int = 32
    learning_rate: float = 0.001
    epochs: int = 50
    
    # Model-specific settings
    cnn_image_size: int = 128
    lstm_hidden_size: int = 128
    lstm_layers: int = 2
    
    # XGBoost settings
    xgb_max_depth: int = 6
    xgb_learning_rate: float = 0.1
    xgb_n_estimators: int = 300
    xgb_subsample: float = 0.8
    xgb_colsample_bytree: float = 0.8
    
    # Anti-overfitting
    walk_forward_initial_train: int = 500
    walk_forward_val_size: int = 100
    walk_forward_step: int = 50
    
    early_stopping_patience: int = 15
    early_stopping_delta: float = 0.001
    
    overfitting_threshold: float = 0.10
    incremental_replay_ratio: float = 0.30
    stochastic_shuffle_ratio: float = 0.10
    
    # Feature engineering
    ta_indicators_lookback: int = 50
    rsi_periods: List[int] = None
    macd_fast: int = 12
    macd_slow: int = 26
    macd_signal: int = 9
    
    # Markets
    supported_markets: List[str] = None
    us_market_hours: tuple = ("09:30", "16:00")  # EST
    india_market_hours: tuple = ("09:15", "15:30")  # IST
    
    # Model versioning
    keep_best_n_versions: int = 5
    auto_backup: bool = True
    
    # Performance thresholds
    min_prediction_confidence: float = 0.55
    max_position_size: float = 0.05  # 5% of portfolio
    
    def __post_init__(self):
        if self.ensemble_weights is None:
            self.ensemble_weights = {
                "cnn": 0.25,
                "lstm": 0.35,
                "xgboost": 0.40,
            }
        
        if self.supported_markets is None:
            self.supported_markets = ["US", "NSE", "BSE"]
        
        if self.rsi_periods is None:
            self.rsi_periods = [7, 14]


# Global config instance
_config = None


def get_ml_config() -> MLConfig:
    """Get global ML configuration"""
    global _config
    if _config is None:
        _config = MLConfig()
    return _config


def set_ml_config(config: MLConfig):
    """Set global ML configuration"""
    global _config
    _config = config


class MarketConfig:
    """Market-specific configuration"""
    
    # US Stock Market
    US_STOCKS = {
        "name": "US Stocks",
        "data_folder": "Stocks",
        "file_extension": ".txt",
        "timezone": "America/New_York",
        "trading_hours": ("09:30", "16:00"),
        "is_crypto": False,
        "min_symbol_length": 1,
        "max_symbol_length": 5,
    }
    
    # US ETFs
    US_ETFS = {
        "name": "US ETFs",
        "data_folder": "ETFs",
        "file_extension": ".txt",
        "timezone": "America/New_York",
        "trading_hours": ("09:30", "16:00"),
        "is_crypto": False,
        "min_symbol_length": 1,
        "max_symbol_length": 5,
    }
    
    # Indian NSE (National Stock Exchange)
    NSE = {
        "name": "NSE",
        "data_folder": "SCRIP",
        "file_extension": ".csv",
        "timezone": "Asia/Kolkata",
        "trading_hours": ("09:15", "15:30"),
        "is_crypto": False,
        "min_symbol_length": 1,
        "max_symbol_length": 10,
    }
    
    # Indian BSE (Bombay Stock Exchange)
    BSE = {
        "name": "BSE",
        "data_folder": "INDEX",
        "file_extension": ".csv",
        "timezone": "Asia/Kolkata",
        "trading_hours": ("09:15", "15:30"),
        "is_crypto": False,
        "min_symbol_length": 1,
        "max_symbol_length": 10,
    }
    
    # Cryptocurrency
    CRYPTO = {
        "name": "Cryptocurrency",
        "data_folder": None,
        "file_extension": ".csv",
        "timezone": "UTC",
        "trading_hours": ("00:00", "23:59"),  # 24/7
        "is_crypto": True,
        "min_symbol_length": 1,
        "max_symbol_length": 10,
    }
    
    MARKET_MAP = {
        "US": US_STOCKS,
        "NSE": NSE,
        "BSE": BSE,
        "CRYPTO": CRYPTO,
    }


class FeatureConfig:
    """Technical indicator configuration"""
    
    INDICATOR_PARAMS = {
        "rsi": {"periods": [7, 14]},
        "macd": {"fast": 12, "slow": 26, "signal": 9},
        "bollinger": {"period": 20, "num_std": 2},
        "atr": {"period": 14},
        "stochastic": {"k_period": 14, "d_period": 3},
        "adx": {"period": 14},
        "vortex": {"period": 14},
        "sma": {"periods": [10, 20, 50, 200]},
        "ema": {"periods": [12, 26]},
    }
    
    PATTERN_NAMES = [
        "bullish_engulfing",
        "bearish_engulfing",
        "hammer",
        "inverted_hammer",
        "doji",
        "morning_star",
        "evening_star",
    ]
    
    PRICE_LEVELS = [
        "support_1",
        "support_2",
        "resistance_1",
        "resistance_2",
        "pivot",
    ]


class SignalConfig:
    """Trading signal configuration"""
    
    SIGNALS = {
        0: "SELL",
        1: "HOLD",
        2: "BUY",
    }
    
    SIGNAL_CLASSES = {
        "SELL": 0,
        "HOLD": 1,
        "BUY": 2,
    }
    
    # Confidence thresholds
    HIGH_CONFIDENCE = 0.75
    MEDIUM_CONFIDENCE = 0.60
    LOW_CONFIDENCE = 0.50
    
    # Signal strength mapping
    STRENGTH_MAP = {
        "SELL": {"high": -2.0, "medium": -1.0, "low": -0.5},
        "HOLD": {"high": 0.0, "medium": 0.0, "low": 0.0},
        "BUY": {"high": 2.0, "medium": 1.0, "low": 0.5},
    }


if __name__ == "__main__":
    config = get_ml_config()
    print(f"ML Config: {config}")
    print(f"Ensemble weights: {config.ensemble_weights}")
