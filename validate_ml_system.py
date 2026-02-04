"""
ML System Validation Script
Tests all components to ensure system is ready for deployment
"""

import sys
import logging
from pathlib import Path
from typing import Dict, List, Tuple

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def check_imports() -> Tuple[bool, List[str]]:
    """Check if all required dependencies are installed"""
    logger.info("=" * 60)
    logger.info("Checking imports...")
    logger.info("=" * 60)
    
    required = [
        ("numpy", "NumPy"),
        ("pandas", "Pandas"),
        ("torch", "PyTorch"),
        ("sklearn", "Scikit-learn"),
        ("xgboost", "XGBoost"),
        ("lightgbm", "LightGBM"),
        ("ta", "TA-Lib"),
    ]
    
    missing = []
    
    for module, name in required:
        try:
            __import__(module)
            logger.info(f"✓ {name}")
        except ImportError:
            logger.warning(f"✗ {name} (not installed)")
            missing.append(name)
    
    return len(missing) == 0, missing


def check_files() -> Tuple[bool, List[str]]:
    """Check if all required files exist"""
    logger.info("\n" + "=" * 60)
    logger.info("Checking files...")
    logger.info("=" * 60)
    
    base_path = Path("/home/mayank/Desktop/AI Paper Trading")
    
    required_files = [
        "backend/ai/data_loader.py",
        "backend/ai/feature_engineering.py",
        "backend/ai/cnn_model.py",
        "backend/ai/lstm_model.py",
        "backend/ai/ensemble_model.py",
        "backend/ai/training_pipeline.py",
        "backend/ai/ml_service.py",
        "backend/ai/config.py",
        "backend/ai/examples.py",
        "backend/api/ml.py",
        "backend/api/ai.py",
        "backend/ai/ML_README.md",
    ]
    
    missing = []
    
    for file_path in required_files:
        full_path = base_path / file_path
        if full_path.exists():
            size = full_path.stat().st_size
            logger.info(f"✓ {file_path} ({size} bytes)")
        else:
            logger.warning(f"✗ {file_path} (not found)")
            missing.append(file_path)
    
    return len(missing) == 0, missing


def check_data() -> Tuple[bool, Dict]:
    """Check if data directories exist and have files"""
    logger.info("\n" + "=" * 60)
    logger.info("Checking data directories...")
    logger.info("=" * 60)
    
    data_path = Path("/home/mayank/Desktop/AI Paper Trading/datasets")
    
    info = {
        "data_path_exists": data_path.exists(),
        "total_csvs": 0,
        "total_txts": 0,
        "folders": {},
    }
    
    if data_path.exists():
        logger.info(f"✓ Data path exists: {data_path}")
        
        # Check subdirectories
        subdirs = ["Stocks", "ETFs", "SCRIP", "INDEX"]
        for subdir in subdirs:
            subdir_path = data_path / subdir
            if subdir_path.exists():
                files = list(subdir_path.glob("*"))
                count = len(files)
                info["folders"][subdir] = count
                logger.info(f"  ✓ {subdir}: {count} files")
            else:
                logger.warning(f"  ✗ {subdir}: not found")
        
        # Count root CSV/TXT files
        csvs = list(data_path.glob("*.csv"))
        txts = list(data_path.glob("*.txt"))
        
        info["total_csvs"] = len(csvs)
        info["total_txts"] = len(txts)
        
        logger.info(f"  ✓ Root CSV files: {len(csvs)}")
        logger.info(f"  ✓ Root TXT files: {len(txts)}")
    else:
        logger.warning(f"✗ Data path not found: {data_path}")
    
    return data_path.exists(), info


def check_module_structure() -> Tuple[bool, Dict]:
    """Check if ML modules have expected classes"""
    logger.info("\n" + "=" * 60)
    logger.info("Checking module structure...")
    logger.info("=" * 60)
    
    modules_to_check = {
        "backend.ai.data_loader": ["DataLoader", "DataValidator"],
        "backend.ai.feature_engineering": ["FeatureEngineer", "TechnicalIndicators"],
        "backend.ai.cnn_model": ["CandlestickCNN", "CandlestickPatternDetector"],
        "backend.ai.lstm_model": ["PricePredictionLSTM", "AttentionLayer"],
        "backend.ai.ensemble_model": ["EnsembleModel", "ModelVersionManager"],
        "backend.ai.training_pipeline": ["TrainingPipeline", "WalkForwardValidator"],
        "backend.ai.ml_service": ["MLService"],
    }
    
    results = {}
    
    for module_name, classes in modules_to_check.items():
        logger.info(f"\nModule: {module_name}")
        results[module_name] = {}
        
        try:
            module = __import__(module_name, fromlist=classes)
            for cls_name in classes:
                if hasattr(module, cls_name):
                    logger.info(f"  ✓ {cls_name}")
                    results[module_name][cls_name] = True
                else:
                    logger.warning(f"  ✗ {cls_name} (not found)")
                    results[module_name][cls_name] = False
        except ImportError as e:
            logger.warning(f"  ✗ Import error: {e}")
            results[module_name]["import_error"] = str(e)
    
    all_ok = all(
        all(v for k, v in classes_dict.items() if k != "import_error")
        for classes_dict in results.values()
    )
    
    return all_ok, results


def check_api_endpoints() -> Tuple[bool, List[str]]:
    """Check if API endpoints are properly defined"""
    logger.info("\n" + "=" * 60)
    logger.info("Checking API endpoints...")
    logger.info("=" * 60)
    
    try:
        from backend.api.ml import router
        
        routes = []
        for route in router.routes:
            if hasattr(route, 'path'):
                methods = route.methods if hasattr(route, 'methods') else ['GET']
                route_name = f"{','.join(methods)} {route.path}"
                routes.append(route_name)
                logger.info(f"  ✓ {route_name}")
        
        return len(routes) > 0, routes
    
    except Exception as e:
        logger.warning(f"✗ API check error: {e}")
        return False, []


def check_configuration() -> Tuple[bool, Dict]:
    """Check if configuration is properly set up"""
    logger.info("\n" + "=" * 60)
    logger.info("Checking configuration...")
    logger.info("=" * 60)
    
    try:
        from backend.ai.config import get_ml_config
        
        config = get_ml_config()
        
        config_info = {
            "data_path": config.data_path,
            "model_path": config.model_path,
            "lookback_period": config.lookback_period,
            "lookahead_period": config.lookahead_period,
            "ensemble_weights": config.ensemble_weights,
            "supported_markets": config.supported_markets,
        }
        
        logger.info(f"  ✓ Data path: {config.data_path}")
        logger.info(f"  ✓ Model path: {config.model_path}")
        logger.info(f"  ✓ Lookback: {config.lookback_period} bars")
        logger.info(f"  ✓ Ensemble weights: {config.ensemble_weights}")
        
        return True, config_info
    
    except Exception as e:
        logger.warning(f"✗ Configuration error: {e}")
        return False, {}


def main():
    """Run all validation checks"""
    logger.info("\n\n")
    logger.info("╔" + "=" * 58 + "╗")
    logger.info("║" + " " * 58 + "║")
    logger.info("║" + "ML SYSTEM VALIDATION".center(58) + "║")
    logger.info("║" + " " * 58 + "║")
    logger.info("╚" + "=" * 58 + "╝")
    
    results = {}
    
    # Run all checks
    results["imports"] = check_imports()
    results["files"] = check_files()
    results["data"] = check_data()
    results["modules"] = check_module_structure()
    results["api"] = check_api_endpoints()
    results["config"] = check_configuration()
    
    # Summary
    logger.info("\n\n" + "=" * 60)
    logger.info("VALIDATION SUMMARY")
    logger.info("=" * 60)
    
    checks = {
        "Dependencies": results["imports"][0],
        "Files": results["files"][0],
        "Data": results["data"][0],
        "Module Structure": results["modules"][0],
        "API Endpoints": results["api"][0],
        "Configuration": results["config"][0],
    }
    
    for check_name, passed in checks.items():
        status = "✓ PASS" if passed else "✗ FAIL"
        logger.info(f"{check_name:<30} {status}")
    
    all_passed = all(checks.values())
    
    logger.info("\n" + "=" * 60)
    if all_passed:
        logger.info("✓ ALL CHECKS PASSED - SYSTEM READY FOR DEPLOYMENT")
        logger.info("=" * 60)
        logger.info("\nNext steps:")
        logger.info("1. Train models: python backend/ai/examples.py")
        logger.info("2. Start server: python -m backend.main")
        logger.info("3. Test API: curl http://localhost:8000/api/ai/health")
        return 0
    else:
        logger.error("✗ SOME CHECKS FAILED - PLEASE FIX ISSUES ABOVE")
        logger.info("=" * 60)
        
        if not results["imports"][0]:
            logger.error(f"\nMissing dependencies: {', '.join(results['imports'][1])}")
            logger.error("Install with: pip install <package>")
        
        if not results["files"][0]:
            logger.error(f"\nMissing files: {', '.join(results['files'][1])}")
        
        return 1


if __name__ == "__main__":
    sys.exit(main())
