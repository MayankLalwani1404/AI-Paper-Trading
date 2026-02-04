"""
Example: Training and Using the ML System
Complete walkthrough of the ML pipeline
"""

import asyncio
import logging
from pathlib import Path
from typing import List

from backend.ai.ml_service import MLService, get_ml_service
from backend.ai.config import get_ml_config, MarketConfig

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


async def example_basic_prediction():
    """Example 1: Make a single prediction"""
    logger.info("=== Example 1: Basic Prediction ===")
    
    service = get_ml_service()
    
    # Make prediction for AAPL on daily timeframe
    prediction = await service.predict("AAPL", timeframe="1d")
    
    logger.info(f"AAPL Prediction: {prediction['signal']}")
    logger.info(f"Confidence: {prediction['confidence']:.2%}")
    logger.info(f"Details: {prediction.get('details', {})}")


async def example_batch_predictions():
    """Example 2: Make batch predictions"""
    logger.info("=== Example 2: Batch Predictions ===")
    
    service = get_ml_service()
    
    symbols = ["AAPL", "GOOGL", "MSFT", "TSLA", "NVDA"]
    predictions = await service.predict_batch(symbols, timeframe="1d")
    
    logger.info(f"Predictions for {len(predictions)} symbols:")
    for pred in predictions:
        logger.info(f"{pred['symbol']}: {pred['signal']} ({pred['confidence']:.2%})")


async def example_training():
    """Example 3: Train models on new data"""
    logger.info("=== Example 3: Training Models ===")
    
    service = get_ml_service()
    
    # Train on US market
    logger.info("Starting training on US market...")
    result = await service.train_models(
        markets=["US"],
        epochs=50
    )
    
    if result['status'] == 'success':
        logger.info(f"Training successful!")
        logger.info(f"Model version: {result['version']}")
        logger.info(f"Symbols trained: {result['symbols_trained']}")
    else:
        logger.error(f"Training failed: {result['error']}")


async def example_incremental_retraining():
    """Example 4: Incremental retraining"""
    logger.info("=== Example 4: Incremental Retraining ===")
    
    service = get_ml_service()
    
    # Retrain on recent data from specific symbols
    symbols_to_retrain = ["AAPL", "GOOGL", "MSFT"]
    
    logger.info(f"Performing incremental retraining on {symbols_to_retrain}...")
    result = await service.incremental_retrain(symbols_to_retrain)
    
    if result['status'] == 'success':
        logger.info(f"Incremental retraining successful!")
        logger.info(f"New model version: {result['version']}")
        logger.info(f"New samples processed: {result['new_samples']}")
    else:
        logger.error(f"Retraining failed: {result['error']}")


def example_model_management():
    """Example 5: Model management"""
    logger.info("=== Example 5: Model Management ===")
    
    service = get_ml_service()
    
    # List all available model versions
    versions = service.list_model_versions()
    logger.info(f"Available model versions: {versions}")
    
    # Activate a specific version
    if versions:
        latest_version = versions[-1]
        logger.info(f"Activating model version: {latest_version}")
        result = service.set_active_model(latest_version)
        logger.info(f"Activation result: {result}")


def example_explainability():
    """Example 6: Explain predictions"""
    logger.info("=== Example 6: Explainability ===")
    
    service = get_ml_service()
    
    # Get explanation for AAPL prediction
    explanation = service.explain_prediction("AAPL", timeframe="1d", num_features=5)
    
    if 'error' not in explanation:
        logger.info(f"Top features for AAPL:")
        for feature in explanation['top_features']:
            logger.info(f"  {feature['name']}: {feature['importance']:.4f}")
    else:
        logger.error(f"Explanation error: {explanation['error']}")


def example_evaluation():
    """Example 7: Evaluate model performance"""
    logger.info("=== Example 7: Model Evaluation ===")
    
    service = get_ml_service()
    
    # Evaluate on AAPL
    evaluation = service.evaluate_model("AAPL", timeframe="1d")
    
    if 'error' not in evaluation:
        logger.info(f"Model performance on AAPL:")
        logger.info(f"  Accuracy: {evaluation['accuracy']:.2%}")
        logger.info(f"  Test samples: {evaluation['samples']}")
    else:
        logger.error(f"Evaluation error: {evaluation['error']}")


def example_market_overview():
    """Example 8: Market overview and configuration"""
    logger.info("=== Example 8: Market Configuration ===")
    
    config = get_ml_config()
    
    logger.info(f"Supported markets: {config.supported_markets}")
    logger.info(f"Data path: {config.data_path}")
    logger.info(f"Model path: {config.model_path}")
    
    # Show market-specific configs
    logger.info("\nMarket Configurations:")
    for market_name, market_config in MarketConfig.MARKET_MAP.items():
        logger.info(f"  {market_name}:")
        logger.info(f"    - Data folder: {market_config.get('data_folder', 'N/A')}")
        logger.info(f"    - Timezone: {market_config['timezone']}")
        logger.info(f"    - Trading hours: {market_config['trading_hours']}")


def example_ensemble_weights():
    """Example 9: Understand ensemble model weights"""
    logger.info("=== Example 9: Ensemble Model Architecture ===")
    
    config = get_ml_config()
    
    logger.info("Ensemble weights (how models are combined):")
    total_weight = sum(config.ensemble_weights.values())
    
    for model, weight in config.ensemble_weights.items():
        percentage = (weight / total_weight) * 100
        logger.info(f"  {model}: {weight} ({percentage:.1f}%)")
    
    logger.info("\nModel details:")
    logger.info(f"  CNN: Candlestick pattern recognition from {config.cnn_image_size}x{config.cnn_image_size} images")
    logger.info(f"  LSTM: Time series prediction on {config.lookback_period}-bar sequences")
    logger.info(f"  XGBoost: {config.xgb_n_estimators} boosted trees on 40+ technical indicators")


async def example_full_workflow():
    """Example 10: Full workflow from training to prediction"""
    logger.info("=== Example 10: Full ML Workflow ===")
    
    service = get_ml_service()
    
    try:
        # Step 1: Train models
        logger.info("Step 1: Training models...")
        train_result = await service.train_models(markets=["US"], epochs=20)
        if train_result['status'] != 'success':
            logger.error(f"Training failed: {train_result['error']}")
            return
        
        logger.info(f"✓ Training successful (version: {train_result['version']})")
        
        # Step 2: Make predictions
        logger.info("Step 2: Making predictions...")
        prediction = await service.predict("AAPL", timeframe="1d")
        logger.info(f"✓ AAPL prediction: {prediction['signal']} ({prediction['confidence']:.2%})")
        
        # Step 3: Get explanations
        logger.info("Step 3: Getting explanations...")
        explanation = service.explain_prediction("AAPL", timeframe="1d", num_features=3)
        if 'top_features' in explanation:
            logger.info(f"✓ Top features: {[f['name'] for f in explanation['top_features']]}")
        
        # Step 4: Evaluate
        logger.info("Step 4: Evaluating model...")
        evaluation = service.evaluate_model("AAPL", timeframe="1d")
        if 'accuracy' in evaluation:
            logger.info(f"✓ Model accuracy: {evaluation['accuracy']:.2%}")
        
        logger.info("\n✓ Full workflow completed successfully!")
        
    except Exception as e:
        logger.error(f"Workflow error: {e}")


async def main():
    """Run all examples"""
    logger.info("Starting ML System Examples\n")
    
    # Run examples
    examples = [
        ("Basic Prediction", example_basic_prediction),
        ("Batch Predictions", example_batch_predictions),
        ("Training", example_training),
        ("Incremental Retraining", example_incremental_retraining),
        ("Model Management", example_model_management),
        ("Explainability", example_explainability),
        ("Evaluation", example_evaluation),
        ("Market Overview", example_market_overview),
        ("Ensemble Weights", example_ensemble_weights),
        ("Full Workflow", example_full_workflow),
    ]
    
    for i, (name, example_func) in enumerate(examples, 1):
        logger.info(f"\n{'='*60}")
        logger.info(f"Running example {i}: {name}")
        logger.info(f"{'='*60}\n")
        
        try:
            if asyncio.iscoroutinefunction(example_func):
                await example_func()
            else:
                example_func()
        except Exception as e:
            logger.error(f"Example '{name}' failed: {e}")
            logger.debug("", exc_info=True)
        
        logger.info("")


if __name__ == "__main__":
    asyncio.run(main())
