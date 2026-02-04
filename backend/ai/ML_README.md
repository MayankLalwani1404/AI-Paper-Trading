# ML Trading System Documentation

## Overview

The AI Paper Trading system includes a comprehensive **hybrid machine learning ensemble** for generating trading signals. The system combines:

1. **CNN** - Candlestick pattern recognition from image data
2. **LSTM** - Time-series direction prediction with attention
3. **XGBoost** - Classification on 40+ technical indicators
4. **Ensemble** - Weighted voting (CNN 0.25 + LSTM 0.35 + XGBoost 0.40)

All models include **anti-overfitting measures**, **transfer learning**, and **explainability** features.

---

## Architecture

### 1. Data Pipeline (`data_loader.py`)

**Purpose**: Load and validate market data from multiple sources

**Features**:
- Multi-format support: CSV, TXT, HuggingFace datasets
- 4,900+ US stocks (Stocks/ folder)
- 900+ US ETFs (ETFs/ folder)
- 52+ Indian indices (INDEX/ folder)
- NSE stocks (SCRIP/ folder)
- Cryptocurrency data (BTCUSDT)

**Key Methods**:
```python
# Load all symbols from a market
all_data = data_loader.load_all_symbols("US")

# Resample to different timeframes
df_1h = data_loader.resample_to_timeframe(df, "1h")

# Split data without temporal leakage
X_train, y_train = split_train_test(df, train_ratio=0.8)

# Validate data quality
data_loader.validate(df)
```

**Anti-Leakage Protections**:
- No forward-fill in missing data
- Separate normalization per train/test fold
- Timeframe resampling prevents lookahead bias
- Gap detection prevents training on incomplete data

---

### 2. Feature Engineering (`feature_engineering.py`)

**Purpose**: Extract 40+ technical indicators and candlestick patterns

**Technical Indicators**:

| Category | Indicators |
|----------|-----------|
| Momentum | RSI(7, 14), MACD, Stochastic |
| Trend | SMA(10,20,50,200), EMA(12,26), ADX |
| Volatility | ATR(14), Bollinger Bands, Vortex |
| Volume | Volume SMA, Volume Oscillator, OBV, PVT |
| Price Action | Wicks, Body ranges, Support/Resistance |

**Candlestick Patterns**:
- Bullish Engulfing
- Bearish Engulfing  
- Hammer / Inverted Hammer
- Doji
- Morning Star / Evening Star

**Key Methods**:
```python
# Create all features from OHLCV data
features_df = feature_engineer.create_features(df_ohlcv)

# Get feature importance names
feature_names = feature_engineer.get_feature_importance_names()
```

**Zero Lookahead Bias**:
- All indicators computed from historical data only
- No future prices used in feature calculation
- Patterns detected from complete candles

---

### 3. CNN Model (`cnn_model.py`)

**Purpose**: Recognize candlestick patterns from chart images

**Architecture**:
```
Input: 128×128 RGB candlestick images
  ↓
Conv Block 1: 32 → 64 filters, BatchNorm, ReLU, MaxPool, Dropout
Conv Block 2: 64 → 128 filters, BatchNorm, MaxPool
Conv Block 3: 128 → 256 filters, BatchNorm, AdaptiveAvgPool
  ↓
Classifier: 256 → ReLU → num_classes output
  ↓
Output: (pattern_class, confidence)
```

**Training**:
- PyTorch + Adam optimizer
- ReduceLROnPlateau scheduler
- Dynamic Learning Rate adjustment
- Dropout prevents overfitting (p=0.5)

**Image Generation**:
- Automatic candlestick image generation from OHLCV
- Normalized price ranges (0-255)
- Volume visualization included
- 128×128 RGB format

---

### 4. LSTM Model (`lstm_model.py`)

**Purpose**: Predict price direction (UP/DOWN/SIDEWAYS)

**Architecture**:
```
Input: (batch_size, 50, 60) sequences
  ↓
LSTM Layer 1: 128 hidden units
LSTM Layer 2: 128 hidden units
  ↓
Attention: 4-head MultiheadAttention
  ↓
Classification Head: 3-way softmax (UP/DOWN/SIDEWAYS)
Confidence Head: Sigmoid regression (0-1)
  ↓
Output: (direction, confidence)
```

**Training**:
- Weighted CrossEntropyLoss for class imbalance
- BCELoss for confidence regression
- Dual-head architecture
- Class weights adapt to market regime

**Transfer Learning**:
- Layer freezing for fine-tuning on new symbols
- Preserves learned temporal patterns
- Reduces training time on new data

---

### 5. Ensemble Model (`ensemble_model.py`)

**Purpose**: Combine predictions from all models

**Voting Mechanism**:
```
Signal = argmax(
    0.25 * CNN_probs +
    0.35 * LSTM_probs +
    0.40 * XGBoost_probs
)
```

**Model Versions**:
```python
# Save model version
version_tag = model_manager.save_version(ensemble_model)
# Returns: "20260204_143022"

# List all versions
versions = model_manager.list_versions()

# Load specific version
model = model_manager.load_version("20260204_143022")
```

**Output Format**:
```python
{
    "signal": "BUY",
    "confidence": 0.78,
    "details": {
        "cnn_probs": [0.2, 0.3, 0.5],
        "lstm_probs": [0.1, 0.2, 0.7],
        "xgb_probs": [0.15, 0.25, 0.6]
    }
}
```

---

### 6. Training Pipeline (`training_pipeline.py`)

**Purpose**: Orchestrate training with anti-overfitting measures

**Walk-Forward Validation**:
```
Initial Train: 500 bars
Validation: 100 bars
Step: 50 bars
(No shuffling, maintains temporal structure)
```

**Overfitting Detection**:
- Monitors train/val loss divergence
- Early stopping (patience=15 epochs)
- Threshold: 10% divergence

**Incremental Learning**:
- Experience replay: Mix 30% old data with new
- Progressive resizing: Gradually increase training set
- Prevents catastrophic forgetting

**Market Regime Detection**:
- Detects BULL/BEAR/SIDEWAYS markets
- Adaptive class weights per regime
- Adjusts model confidence based on market state

**Stochastic Batch Shuffling**:
- 10% of samples randomly shuffled
- Preserves temporal structure
- Light augmentation prevents overfitting

---

## API Endpoints

### Prediction Endpoints

#### POST `/api/ai/predict`
Make a single prediction for a symbol

```json
Request:
{
    "symbol": "AAPL",
    "timeframe": "1d"
}

Response:
{
    "symbol": "AAPL",
    "signal": "BUY",
    "confidence": 0.78,
    "timestamp": "2025-02-04T14:30:22",
    "details": {...}
}
```

#### POST `/api/ai/predict-batch`
Make predictions for multiple symbols

```
POST /api/ai/predict-batch?symbols=AAPL&symbols=GOOGL&symbols=MSFT&timeframe=1d

Response:
{
    "predictions": [
        {"symbol": "AAPL", "signal": "BUY", "confidence": 0.78, ...},
        {"symbol": "GOOGL", "signal": "HOLD", "confidence": 0.55, ...},
        {"symbol": "MSFT", "signal": "SELL", "confidence": 0.72", ...}
    ]
}
```

---

### Training Endpoints

#### POST `/api/ai/train`
Train models on specified markets

```json
Request:
{
    "markets": ["US", "NSE"],
    "epochs": 50
}

Response:
{
    "status": "success",
    "version": "20250204_143022",
    "symbols_trained": 156,
    "total_samples": 45000,
    "timestamp": "2025-02-04T14:30:22"
}
```

#### POST `/api/ai/retrain-incremental`
Perform incremental retraining with new data

```
POST /api/ai/retrain-incremental?symbols=AAPL&symbols=GOOGL

Response:
{
    "status": "success",
    "version": "incremental_20250204_143022",
    "new_samples": 2000,
    "timestamp": "2025-02-04T14:30:22"
}
```

---

### Model Management

#### GET `/api/ai/models`
List available model versions

```json
Response:
{
    "versions": [
        "20250201_100000",
        "20250203_120000",
        "20250204_143022"
    ]
}
```

#### POST `/api/ai/models/{version}/activate`
Activate a specific model version

```
POST /api/ai/models/20250204_143022/activate

Response:
{
    "status": "success",
    "active_version": "20250204_143022"
}
```

---

### Explainability

#### GET `/api/ai/explain/{symbol}`
Explain prediction using SHAP values

```
GET /api/ai/explain/AAPL?timeframe=1d&num_features=5

Response:
{
    "symbol": "AAPL",
    "top_features": [
        {"name": "RSI_14", "importance": 0.245},
        {"name": "MACD", "importance": 0.198},
        {"name": "ATR_14", "importance": 0.156},
        {"name": "Bollinger_Band", "importance": 0.134},
        {"name": "Volume_SMA", "importance": 0.098}
    ],
    "method": "SHAP"
}
```

---

### Evaluation

#### GET `/api/ai/evaluate/{symbol}`
Evaluate model performance on a symbol

```
GET /api/ai/evaluate/AAPL?timeframe=1d

Response:
{
    "symbol": "AAPL",
    "accuracy": 0.62,
    "samples": 250,
    "timestamp": "2025-02-04T14:30:22"
}
```

#### GET `/api/ai/health`
Health check for ML service

```json
Response:
{
    "status": "healthy",
    "service": "ml",
    "models_available": 3
}
```

---

## Usage Examples

### Example 1: Basic Prediction

```python
from backend.ai.ml_service import get_ml_service
import asyncio

async def predict_stock():
    service = get_ml_service()
    prediction = await service.predict("AAPL", timeframe="1d")
    print(f"Signal: {prediction['signal']}")
    print(f"Confidence: {prediction['confidence']:.2%}")

asyncio.run(predict_stock())
```

### Example 2: Train Models

```python
async def train_models():
    service = get_ml_service()
    result = await service.train_models(
        markets=["US"],
        epochs=50
    )
    print(f"Model version: {result['version']}")
    print(f"Symbols trained: {result['symbols_trained']}")

asyncio.run(train_models())
```

### Example 3: Explain Prediction

```python
def explain():
    service = get_ml_service()
    explanation = service.explain_prediction("AAPL")
    
    for feature in explanation['top_features']:
        print(f"{feature['name']}: {feature['importance']:.4f}")

explain()
```

### Example 4: Batch Predictions

```python
async def batch_predict():
    service = get_ml_service()
    symbols = ["AAPL", "GOOGL", "MSFT", "TSLA"]
    predictions = await service.predict_batch(symbols)
    
    for pred in predictions:
        print(f"{pred['symbol']}: {pred['signal']}")

asyncio.run(batch_predict())
```

---

## Configuration

All ML settings are in `backend/ai/config.py`:

```python
from backend.ai.config import get_ml_config

config = get_ml_config()

# Data paths
config.data_path = "datasets"
config.model_path = "ml_models"

# Model sizes
config.cnn_image_size = 128
config.lstm_hidden_size = 128

# Training parameters
config.epochs = 50
config.batch_size = 32
config.learning_rate = 0.001

# Anti-overfitting
config.early_stopping_patience = 15
config.overfitting_threshold = 0.10

# Ensemble weights
config.ensemble_weights = {
    "cnn": 0.25,
    "lstm": 0.35,
    "xgboost": 0.40,
}
```

---

## Supported Markets

| Market | Symbols | Data Folder | Format |
|--------|---------|------------|--------|
| US Stocks | 4000+ | Stocks/ | .txt |
| US ETFs | 900+ | ETFs/ | .txt |
| NSE (India) | 1000+ | SCRIP/ | .csv |
| BSE (India) | 52 | INDEX/ | .csv |
| Crypto | BTCUSDT | - | .csv |

---

## Data Quality Checks

The system automatically validates data:

1. **Gap Detection**: Identifies missing bars
2. **Outlier Detection**: Flags unusual price moves
3. **Stationarity Testing**: Checks if data is stationary
4. **Volume Validation**: Ensures volume data exists
5. **Timestamp Validation**: Verifies consistent intervals

---

## Performance Optimization

### Model Inference
- Cached predictions (1-minute window)
- Batch processing support
- Async/await for non-blocking operations

### Training
- Walk-forward validation reduces full-retraining
- Incremental learning for daily updates
- Transfer learning speeds up new symbol training

### Storage
- Model versioning keeps best N versions
- Automatic backups of trained models
- JSON metadata for quick version lookup

---

## Troubleshooting

### Issue: Low Prediction Confidence
**Cause**: Market is in uncertain regime (low volatility, sideways movement)
**Solution**: Wait for clearer trends or increase position risk

### Issue: Model Not Improving
**Cause**: Data distribution has changed (regime shift)
**Solution**: Perform incremental retraining with recent data

### Issue: Memory Error During Training
**Cause**: Too much data or too large batch size
**Solution**: Reduce batch size or limit symbols in training

---

## System Requirements

```
Python: 3.9+
PyTorch: 2.0+
XGBoost: 2.0+
LightGBM: 4.0+
NumPy: 1.20+
Pandas: 1.3+
Scikit-learn: 1.0+
TA-Lib: 0.4+
SHAP: 0.42+
```

---

## Next Steps

1. **Run Training**: Execute `backend/ai/examples.py`
2. **Deploy API**: Start FastAPI server
3. **Monitor Performance**: Check `/api/ai/health`
4. **Retrain Daily**: Use `/api/ai/retrain-incremental`
5. **Analyze Signals**: Use `/api/ai/explain/{symbol}` for insights

---

## Files

| File | Purpose |
|------|---------|
| `data_loader.py` | Data loading and validation |
| `feature_engineering.py` | Technical indicator extraction |
| `cnn_model.py` | Candlestick pattern CNN |
| `lstm_model.py` | Time-series LSTM with attention |
| `ensemble_model.py` | Model combining and versioning |
| `training_pipeline.py` | Training orchestration |
| `ml_service.py` | Service wrapper for all models |
| `config.py` | Configuration and constants |
| `examples.py` | Usage examples |

