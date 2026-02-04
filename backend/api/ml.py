"""
FastAPI Routes for ML Service
Integrates ML models with REST API endpoints
"""

from fastapi import APIRouter, HTTPException, Query
from typing import List, Optional
from pydantic import BaseModel
import logging
import asyncio

from backend.ai.ml_service import get_ml_service

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/ai", tags=["ai"])


# ===== Request/Response Models =====

class PredictionRequest(BaseModel):
    symbol: str
    timeframe: str = "1d"
    

class PredictionResponse(BaseModel):
    symbol: str
    signal: Optional[str]
    confidence: float
    timestamp: str
    details: Optional[dict] = None
    

class TrainingRequest(BaseModel):
    markets: List[str] = ["US", "NSE"]
    epochs: int = 50
    

class TrainingResponse(BaseModel):
    status: str
    version: Optional[str] = None
    symbols_trained: Optional[int] = None
    error: Optional[str] = None
    

class ModelVersionResponse(BaseModel):
    versions: List[str]
    

class ExplanationResponse(BaseModel):
    symbol: str
    top_features: List[dict]
    method: str
    

class EvaluationResponse(BaseModel):
    symbol: str
    accuracy: Optional[float] = None
    samples: Optional[int] = None
    error: Optional[str] = None


# ===== Prediction Endpoints =====

@router.post("/predict", response_model=PredictionResponse)
async def predict(request: PredictionRequest):
    """
    Make prediction for a stock symbol
    
    Args:
        symbol: Stock symbol (e.g., 'AAPL', 'ADANIPORTS')
        timeframe: Timeframe (1m, 5m, 15m, 1h, 1d, 1w, 1M)
    
    Returns:
        Prediction with signal (BUY/SELL/HOLD) and confidence
    """
    try:
        service = get_ml_service()
        result = await service.predict(request.symbol, request.timeframe)
        
        if 'error' in result:
            raise HTTPException(status_code=400, detail=result['error'])
        
        return PredictionResponse(**result)
    except Exception as e:
        logger.error(f"Prediction endpoint error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/predict-batch")
async def predict_batch(symbols: List[str] = Query(...), 
                       timeframe: str = "1d"):
    """
    Make predictions for multiple symbols
    
    Args:
        symbols: List of stock symbols
        timeframe: Timeframe (default: 1d)
    
    Returns:
        List of predictions
    """
    try:
        service = get_ml_service()
        results = await service.predict_batch(symbols, timeframe)
        return {"predictions": results}
    except Exception as e:
        logger.error(f"Batch prediction error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ===== Training Endpoints =====

@router.post("/train", response_model=TrainingResponse)
async def train(request: TrainingRequest):
    """
    Train ML models on specified markets
    
    Args:
        markets: List of markets ('US', 'NSE', 'BSE')
        epochs: Number of training epochs
    
    Returns:
        Training status and model version
    """
    try:
        service = get_ml_service()
        result = await service.train_models(request.markets, request.epochs)
        return TrainingResponse(**result)
    except Exception as e:
        logger.error(f"Training endpoint error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/retrain-incremental")
async def retrain_incremental(symbols: List[str] = Query(...)):
    """
    Perform incremental retraining with new data
    
    Args:
        symbols: Symbols to retrain on
    
    Returns:
        Retraining status and new model version
    """
    try:
        service = get_ml_service()
        result = await service.incremental_retrain(symbols)
        return result
    except Exception as e:
        logger.error(f"Incremental retraining error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ===== Model Management Endpoints =====

@router.get("/models", response_model=ModelVersionResponse)
async def list_models():
    """
    List all available model versions
    
    Returns:
        List of model version tags
    """
    try:
        service = get_ml_service()
        versions = service.list_model_versions()
        return ModelVersionResponse(versions=versions)
    except Exception as e:
        logger.error(f"Model listing error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/models/{version}/activate")
async def activate_model(version: str):
    """
    Activate a specific model version
    
    Args:
        version: Version tag to activate
    
    Returns:
        Activation status
    """
    try:
        service = get_ml_service()
        result = service.set_active_model(version)
        if result['status'] != 'success':
            raise HTTPException(status_code=400, detail=result.get('error', 'Failed to activate model'))
        return result
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Model activation error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ===== Explainability Endpoints =====

@router.get("/explain/{symbol}", response_model=ExplanationResponse)
async def explain(symbol: str, 
                 timeframe: str = "1d",
                 num_features: int = 10):
    """
    Explain prediction for a symbol using SHAP
    
    Args:
        symbol: Stock symbol
        timeframe: Timeframe (default: 1d)
        num_features: Number of top features to return
    
    Returns:
        Top features influencing the prediction
    """
    try:
        service = get_ml_service()
        result = service.explain_prediction(symbol, timeframe, num_features)
        
        if 'error' in result:
            raise HTTPException(status_code=400, detail=result['error'])
        
        return ExplanationResponse(**result)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Explanation error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ===== Evaluation Endpoints =====

@router.get("/evaluate/{symbol}", response_model=EvaluationResponse)
async def evaluate(symbol: str, timeframe: str = "1d"):
    """
    Evaluate model performance on a symbol
    
    Args:
        symbol: Stock symbol
        timeframe: Timeframe (default: 1d)
    
    Returns:
        Model accuracy and performance metrics
    """
    try:
        service = get_ml_service()
        result = service.evaluate_model(symbol, timeframe)
        
        if 'error' in result:
            raise HTTPException(status_code=400, detail=result['error'])
        
        return EvaluationResponse(**result)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Evaluation error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ===== Health Check =====

@router.get("/health")
async def health():
    """
    Health check for ML service
    
    Returns:
        Service status
    """
    try:
        service = get_ml_service()
        return {
            "status": "healthy",
            "service": "ml",
            "models_available": len(service.list_model_versions()),
        }
    except Exception as e:
        logger.error(f"Health check error: {e}")
        return {
            "status": "unhealthy",
            "service": "ml",
            "error": str(e),
        }


if __name__ == "__main__":
    logger.info("ML API routes ready for FastAPI integration")
