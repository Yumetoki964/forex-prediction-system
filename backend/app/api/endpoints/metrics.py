"""
Risk Metrics API Endpoints
==========================

Phase B-2aの対象エンドポイント:
- 1.4: /api/metrics/risk (GET) - リスク指標取得

仮実装でレスポンスを返し、後のサービス層実装で置き換え予定
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime, date, timedelta

from ...database import get_db
from ...schemas.metrics import (
    RiskMetricsResponse,
    VolatilityMetrics,
    ValueAtRisk,
    DrawdownMetrics,
    CorrelationMetrics,
    RiskDecomposition,
    StressTestScenario,
    RiskLevel,
    VolatilityRegime,
    TimeHorizon
)
from ...services.metrics_service import MetricsService

router = APIRouter()


# ===================================================================
# 1.4: /api/metrics/risk (GET) - リスク指標取得
# ===================================================================

@router.get("/risk", response_model=RiskMetricsResponse)
async def get_risk_metrics(
    time_horizon: Optional[TimeHorizon] = Query(TimeHorizon.DAILY, description="リスク評価期間"),
    confidence_level: float = Query(0.95, description="VaR信頼水準", ge=0.9, le=0.99),
    include_stress_test: bool = Query(True, description="ストレステストを含める"),
    db: Session = Depends(get_db)
) -> RiskMetricsResponse:
    """
    包括的なリスク指標を取得
    
    - **time_horizon**: リスク評価の時間軸
    - **confidence_level**: VaR計算の信頼水準
    - **include_stress_test**: ストレステストシナリオを含める
    - **returns**: ボラティリティ、VaR、ドローダウン等の総合リスク分析
    """
    
    try:
        service = MetricsService(db)
        return await service.get_risk_metrics(time_horizon, confidence_level, include_stress_test)
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"リスク指標の計算中にエラーが発生しました: {str(e)}"
        )


# ===================================================================
# リスクサマリーエンドポイント
# ===================================================================

@router.get("/risk/summary")
async def get_risk_summary(db: Session = Depends(get_db)):
    """リスク指標のサマリーを取得"""
    try:
        return {
            "overall_risk": "MEDIUM",
            "key_risks": [
                "中央銀行政策変更リスク",
                "地政学的不確実性",
                "市場ボラティリティ上昇"
            ],
            "risk_score": 45.8,
            "last_updated": datetime.now()
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"リスクサマリーの取得中にエラーが発生しました: {str(e)}"
        )


# ===================================================================
# ヘルスチェック
# ===================================================================

@router.get("/health")
async def metrics_health_check():
    """メトリクスAPIのヘルスチェック"""
    return {
        "status": "healthy",
        "service": "metrics",
        "timestamp": datetime.now(),
        "version": "1.0.0"
    }