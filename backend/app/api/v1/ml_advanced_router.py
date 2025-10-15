"""
Advanced ML Router
FastAPI router for advanced machine learning model endpoints
"""

from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from fastapi.responses import JSONResponse
from typing import Dict, Any, Optional
import logging

from ml.services.advanced_ml_service import advanced_ml_service
from auth.middleware import get_current_user
from auth.models import User

logger = logging.getLogger(__name__)

ml_advanced_router = APIRouter(prefix="/ml/advanced", tags=["Advanced ML Models"])


@ml_advanced_router.on_event("startup")
async def startup_event():
    """Initialize ML models on startup"""
    try:
        await advanced_ml_service.initialize_models()
        logger.info("✅ Advanced ML models initialized on startup")
    except Exception as e:
        logger.error(f"❌ Failed to initialize ML models: {e}")


@ml_advanced_router.post("/models/initialize")
async def initialize_models(
    current_user: User = Depends(get_current_user),
) -> Dict[str, Any]:
    """Initialize or reinitialize all ML models"""
    try:
        if current_user.role not in ["admin", "agent"]:
            raise HTTPException(status_code=403, detail="Insufficient permissions")

        success = await advanced_ml_service.initialize_models()

        if success:
            return {
                "status": "success",
                "message": "ML models initialized successfully",
                "models_count": len(advanced_ml_service.current_models),
            }
        else:
            raise HTTPException(
                status_code=500, detail="Failed to initialize ML models"
            )

    except Exception as e:
        logger.error(f"❌ Error initializing models: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@ml_advanced_router.post("/models/train/{model_name}")
async def train_model(
    model_name: str,
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_current_user),
) -> Dict[str, Any]:
    """Train a specific ML model"""
    try:
        if current_user.role not in ["admin", "agent"]:
            raise HTTPException(status_code=403, detail="Insufficient permissions")

        if model_name not in advanced_ml_service.current_models:
            raise HTTPException(status_code=404, detail=f"Model {model_name} not found")

        # Start training in background
        background_tasks.add_task(advanced_ml_service.train_model, model_name)

        return {
            "status": "success",
            "message": f"Training started for {model_name} model",
            "model_name": model_name,
            "background_task": True,
        }

    except Exception as e:
        logger.error(f"❌ Error starting model training: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@ml_advanced_router.post("/models/train-all")
async def train_all_models(
    background_tasks: BackgroundTasks, current_user: User = Depends(get_current_user)
) -> Dict[str, Any]:
    """Train all available ML models"""
    try:
        if current_user.role not in ["admin", "agent"]:
            raise HTTPException(status_code=403, detail="Insufficient permissions")

        # Start training all models in background
        for model_name in advanced_ml_service.current_models.keys():
            background_tasks.add_task(advanced_ml_service.train_model, model_name)

        return {
            "status": "success",
            "message": f"Training started for {len(advanced_ml_service.current_models)} models",
            "models": list(advanced_ml_service.current_models.keys()),
            "background_task": True,
        }

    except Exception as e:
        logger.error(f"❌ Error starting model training: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@ml_advanced_router.post("/models/retrain")
async def retrain_models(
    force_retrain: bool = False,
    background_tasks: BackgroundTasks = None,
    current_user: User = Depends(get_current_user),
) -> Dict[str, Any]:
    """Retrain all models with fresh data"""
    try:
        if current_user.role not in ["admin", "agent"]:
            raise HTTPException(status_code=403, detail="Insufficient permissions")

        if background_tasks:
            # Start retraining in background
            background_tasks.add_task(advanced_ml_service.retrain_models, force_retrain)
            return {
                "status": "success",
                "message": "Model retraining started in background",
                "force_retrain": force_retrain,
                "background_task": True,
            }
        else:
            # Run synchronously
            result = await advanced_ml_service.retrain_models(force_retrain)
            return result

    except Exception as e:
        logger.error(f"❌ Error retraining models: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@ml_advanced_router.post("/models/optimize/{model_name}")
async def optimize_model_hyperparameters(
    model_name: str,
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_current_user),
) -> Dict[str, Any]:
    """Optimize hyperparameters for a specific model"""
    try:
        if current_user.role not in ["admin", "agent"]:
            raise HTTPException(status_code=403, detail="Insufficient permissions")

        if model_name not in advanced_ml_service.current_models:
            raise HTTPException(status_code=404, detail=f"Model {model_name} not found")

        # Start optimization in background
        background_tasks.add_task(
            advanced_ml_service.optimize_model_hyperparameters, model_name
        )

        return {
            "status": "success",
            "message": f"Hyperparameter optimization started for {model_name}",
            "model_name": model_name,
            "background_task": True,
        }

    except Exception as e:
        logger.error(f"❌ Error starting hyperparameter optimization: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@ml_advanced_router.post("/predict/property-price")
async def predict_property_price(
    property_features: Dict[str, Any],
    model_name: str = "ensemble",
    current_user: User = Depends(get_current_user),
) -> Dict[str, Any]:
    """Predict property price using trained ML models"""
    try:
        if not property_features:
            raise HTTPException(
                status_code=400, detail="Property features are required"
            )

        # Validate required features
        required_features = ["property_size", "bedrooms", "bathrooms"]
        missing_features = [f for f in required_features if f not in property_features]

        if missing_features:
            raise HTTPException(
                status_code=400,
                detail=f"Missing required features: {', '.join(missing_features)}",
            )

        # Make prediction
        prediction = await advanced_ml_service.predict_property_price(
            property_features, model_name
        )

        if "error" in prediction:
            raise HTTPException(status_code=500, detail=prediction["error"])

        return {
            "status": "success",
            "prediction": prediction,
            "user_id": current_user.id,
            "timestamp": prediction["prediction_timestamp"],
        }

    except Exception as e:
        logger.error(f"❌ Error making property price prediction: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@ml_advanced_router.get("/models/performance")
async def get_model_performance(
    model_name: Optional[str] = None, current_user: User = Depends(get_current_user)
) -> Dict[str, Any]:
    """Get performance metrics for ML models"""
    try:
        performance = await advanced_ml_service.get_model_performance(model_name)

        if "error" in performance:
            raise HTTPException(status_code=500, detail=performance["error"])

        return {"status": "success", "performance": performance}

    except Exception as e:
        logger.error(f"❌ Error getting model performance: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@ml_advanced_router.get("/models/insights")
async def get_model_insights(
    current_user: User = Depends(get_current_user),
) -> Dict[str, Any]:
    """Get comprehensive insights about all ML models"""
    try:
        insights = await advanced_ml_service.get_model_insights()

        if "error" in insights:
            raise HTTPException(status_code=500, detail=insights["error"])

        return {"status": "success", "insights": insights}

    except Exception as e:
        logger.error(f"❌ Error getting model insights: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@ml_advanced_router.get("/models/status")
async def get_models_status(
    current_user: User = Depends(get_current_user),
) -> Dict[str, Any]:
    """Get current status of all ML models"""
    try:
        models_status = {}

        for model_name, model_info in advanced_ml_service.current_models.items():
            models_status[model_name] = {
                "status": "trained" if model_info.get("metrics") else "untrained",
                "last_updated": model_info.get("last_updated"),
                "training_samples": model_info.get("training_samples", 0),
                "has_scaler": "scaler" in model_info,
                "file_path": str(model_info.get("file_path"))
                if model_info.get("file_path")
                else None,
            }

        return {
            "status": "success",
            "total_models": len(advanced_ml_service.current_models),
            "models": models_status,
        }

    except Exception as e:
        logger.error(f"❌ Error getting models status: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@ml_advanced_router.post("/models/generate-training-data")
async def generate_training_data(
    num_samples: int = 10000, current_user: User = Depends(get_current_user)
) -> Dict[str, Any]:
    """Generate synthetic training data for model training"""
    try:
        if current_user.role not in ["admin", "agent"]:
            raise HTTPException(status_code=403, detail="Insufficient permissions")

        if num_samples <= 0 or num_samples > 100000:
            raise HTTPException(
                status_code=400,
                detail="Number of samples must be between 1 and 100,000",
            )

        training_data = await advanced_ml_service.generate_synthetic_training_data(
            num_samples
        )

        if training_data.empty:
            raise HTTPException(
                status_code=500, detail="Failed to generate training data"
            )

        return {
            "status": "success",
            "message": f"Generated {len(training_data)} training samples",
            "samples_count": len(training_data),
            "features": list(training_data.columns),
            "data_preview": training_data.head(5).to_dict("records"),
        }

    except Exception as e:
        logger.error(f"❌ Error generating training data: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@ml_advanced_router.delete("/models/{model_name}")
async def delete_model(
    model_name: str, current_user: User = Depends(get_current_user)
) -> Dict[str, Any]:
    """Delete a specific ML model"""
    try:
        if current_user.role != "admin":
            raise HTTPException(status_code=403, detail="Only admins can delete models")

        if model_name not in advanced_ml_service.current_models:
            raise HTTPException(status_code=404, detail=f"Model {model_name} not found")

        # Remove model from memory
        del advanced_ml_service.current_models[model_name]

        # TODO: Delete model files from disk

        return {
            "status": "success",
            "message": f"Model {model_name} deleted successfully",
            "deleted_model": model_name,
        }

    except Exception as e:
        logger.error(f"❌ Error deleting model {model_name}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@ml_advanced_router.get("/health")
async def health_check() -> Dict[str, Any]:
    """Health check endpoint for advanced ML service"""
    try:
        models_count = len(advanced_ml_service.current_models)
        active_models = sum(
            1
            for info in advanced_ml_service.current_models.values()
            if info.get("metrics")
        )

        return {
            "status": "healthy",
            "service": "Advanced ML Service",
            "models_loaded": models_count,
            "active_models": active_models,
            "timestamp": advanced_ml_service.current_models.get("timestamp", "unknown"),
        }

    except Exception as e:
        logger.error(f"❌ Health check failed: {e}")
        return {
            "status": "unhealthy",
            "service": "Advanced ML Service",
            "error": str(e),
        }
