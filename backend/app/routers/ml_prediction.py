"""
機械学習予測APIエンドポイント
"""
from fastapi import APIRouter, HTTPException, Depends, Query, BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Dict, Any, List, Optional
import logging

from app.database import get_db
from app.services.prediction_service import PredictionService
from app.core.dependencies import get_current_user

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/api/ml",
    tags=["ml-prediction"]
)

# グローバルサービスインスタンス
prediction_service = PredictionService()

@router.post("/train")
async def train_model(
    background_tasks: BackgroundTasks,
    currency_pair: str = Query(default="USD/JPY", description="Currency pair"),
    force_retrain: bool = Query(default=False, description="Force retrain even if model exists"),
    db: AsyncSession = Depends(get_db)
    # current_user: dict = Depends(get_current_user)
) -> Dict[str, Any]:
    """
    モデルを訓練（バックグラウンドで実行）
    """
    try:
        # バックグラウンドタスクとして訓練を実行
        background_tasks.add_task(
            prediction_service.train_model,
            db,
            currency_pair,
            force_retrain
        )
        
        return {
            "status": "training_started",
            "message": "Model training has been started in the background",
            "currency_pair": currency_pair
        }
        
    except Exception as e:
        logger.error(f"Error starting model training: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to start model training")

@router.post("/train-sync")
async def train_model_sync(
    currency_pair: str = Query(default="USD/JPY", description="Currency pair"),
    force_retrain: bool = Query(default=False, description="Force retrain even if model exists"),
    db: AsyncSession = Depends(get_db)
    # current_user: dict = Depends(get_current_user)
) -> Dict[str, Any]:
    """
    モデルを訓練（同期実行）
    """
    try:
        result = await prediction_service.train_model(
            db=db,
            currency_pair=currency_pair,
            force_retrain=force_retrain
        )
        
        return result
        
    except Exception as e:
        logger.error(f"Error training model: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to train model")

@router.post("/predict")
async def make_prediction(
    currency_pair: str = Query(default="USD/JPY", description="Currency pair"),
    periods: Optional[List[str]] = Query(default=None, description="Prediction periods"),
    db: AsyncSession = Depends(get_db)
    # current_user: dict = Depends(get_current_user)
) -> Dict[str, Any]:
    """
    為替レート予測を実行
    """
    try:
        result = await prediction_service.predict(
            db=db,
            currency_pair=currency_pair,
            prediction_periods=periods
        )
        
        return result
        
    except Exception as e:
        logger.error(f"Error making prediction: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to make prediction")

@router.get("/model-status")
async def get_model_status() -> Dict[str, Any]:
    """
    モデルのステータスを取得
    """
    try:
        status = await prediction_service.get_model_status()
        return status
        
    except Exception as e:
        logger.error(f"Error getting model status: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to get model status")

@router.post("/load-model")
async def load_model() -> Dict[str, Any]:
    """
    保存されたモデルを読み込み
    """
    try:
        success = await prediction_service.load_model()
        
        if success:
            return {
                "status": "success",
                "message": "Model loaded successfully"
            }
        else:
            return {
                "status": "not_found",
                "message": "Model files not found. Please train the model first."
            }
        
    except Exception as e:
        logger.error(f"Error loading model: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to load model")

@router.get("/supported-pairs")
async def get_supported_pairs() -> Dict[str, List[str]]:
    """
    サポートされている通貨ペアを取得
    """
    return {
        "supported_pairs": ["USD/JPY", "EUR/USD", "GBP/USD", "EUR/JPY"],
        "default": "USD/JPY"
    }

@router.get("/prediction-periods")
async def get_prediction_periods() -> Dict[str, List[Dict[str, str]]]:
    """
    利用可能な予測期間を取得
    """
    return {
        "periods": [
            {"value": "1day", "label": "1日後", "days": 1},
            {"value": "1week", "label": "1週間後", "days": 7},
            {"value": "2weeks", "label": "2週間後", "days": 14},
            {"value": "1month", "label": "1ヶ月後", "days": 30}
        ]
    }