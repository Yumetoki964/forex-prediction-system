"""
Predictions API Endpoints
=========================

Phase B-2aの対象エンドポイント:
- 1.2: /api/predictions/latest (GET) - 最新予測取得
- 2.2: /api/predictions/detailed (GET) - 詳細予測分析取得

仮実装でレスポンスを返し、後のサービス層実装で置き換え予定
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime, date, timedelta

from ...database import get_db
from ...schemas.predictions import (
    LatestPredictionsResponse,
    DetailedPredictionsResponse,
    PredictionItem,
    DetailedPredictionItem,
    MarketCondition,
    ModelAnalysis,
    FeatureImportance,
    PredictionPeriod,
    PredictionModel,
    PredictionErrorResponse
)
from ...models import Prediction
from ...services.predictions_service import PredictionsService

router = APIRouter()


# ===================================================================
# 1.2: /api/predictions/latest (GET) - 最新予測取得
# ===================================================================

@router.get("/latest", response_model=LatestPredictionsResponse)
async def get_latest_predictions(
    periods: Optional[List[PredictionPeriod]] = Query(None, description="取得する予測期間"),
    db: Session = Depends(get_db)
) -> LatestPredictionsResponse:
    """
    最新の予測結果を取得
    
    - **periods**: 取得する予測期間のリスト（未指定時は全期間）
    - **returns**: 1週間〜1ヶ月の予測データと信頼区間
    """
    
    try:
        service = PredictionsService(db)
        return await service.get_latest_predictions(periods)
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"予測データの取得中にエラーが発生しました: {str(e)}"
        )


# ===================================================================
# 2.2: /api/predictions/detailed (GET) - 詳細予測分析取得
# ===================================================================

@router.get("/detailed", response_model=DetailedPredictionsResponse)
async def get_detailed_predictions(
    period: Optional[PredictionPeriod] = Query(PredictionPeriod.ONE_WEEK, description="分析対象期間"),
    include_feature_importance: bool = Query(True, description="特徴量重要度を含める"),
    include_scenario_analysis: bool = Query(True, description="シナリオ分析を含める"),
    db: Session = Depends(get_db)
) -> DetailedPredictionsResponse:
    """
    詳細な予測分析データを取得
    
    - **period**: 分析対象期間
    - **include_feature_importance**: 特徴量重要度分析を含める
    - **include_scenario_analysis**: シナリオ分析を含める
    - **returns**: モデル別分析と詳細な不確実性評価
    """
    
    try:
        service = PredictionsService(db)
        return await service.get_detailed_predictions(period, include_feature_importance, include_scenario_analysis)
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"詳細予測分析の取得中にエラーが発生しました: {str(e)}"
        )


# ===================================================================
# エラーハンドリング
# ===================================================================

@router.get("/health")
async def predictions_health_check():
    """予測APIのヘルスチェック"""
    return {
        "status": "healthy",
        "service": "predictions",
        "timestamp": datetime.now(),
        "version": "1.0.0"
    }