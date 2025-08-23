"""
Technical & Economic Indicators API Endpoints
=============================================

Phase B-2aの対象エンドポイント:
- 2.3: /api/indicators/technical (GET) - テクニカル指標取得
- 2.4: /api/indicators/economic (GET) - 経済指標影響度取得

仮実装でレスポンスを返し、後のサービス層実装で置き換え予定
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime, date, timedelta

from ...database import get_db
from ...schemas.indicators import (
    TechnicalIndicatorsResponse,
    EconomicImpactResponse,
    MovingAverageIndicator,
    OscillatorIndicator,
    MomentumIndicator,
    VolatilityIndicator,
    VolumeIndicator,
    TechnicalSummary,
    EconomicIndicatorItem,
    CentralBankPolicy,
    MacroeconomicTrend,
    MarketSentimentIndicator,
    GeopoliticalRisk,
    EconomicCalendar,
    IndicatorSignal,
    TrendDirection,
    EconomicIndicatorCategory
)
from ...services.indicators_service import IndicatorsService

router = APIRouter()


# ===================================================================
# 2.3: /api/indicators/technical (GET) - テクニカル指標取得
# ===================================================================

@router.get("/technical", response_model=TechnicalIndicatorsResponse)
async def get_technical_indicators(
    analysis_date: Optional[date] = Query(None, description="分析対象日（未指定時は最新）"),
    include_volume: bool = Query(True, description="出来高指標を含める"),
    db: Session = Depends(get_db)
) -> TechnicalIndicatorsResponse:
    """
    テクニカル指標の現在値と推移を取得
    
    - **analysis_date**: 分析対象日
    - **include_volume**: 出来高指標を含めるかどうか
    - **returns**: 移動平均、オシレーター、モメンタム等の総合テクニカル分析
    """
    
    try:
        service = IndicatorsService(db)
        return await service.get_technical_indicators(analysis_date, include_volume)
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"テクニカル指標の計算中にエラーが発生しました: {str(e)}"
        )


# ===================================================================
# 2.4: /api/indicators/economic (GET) - 経済指標影響度取得
# ===================================================================

@router.get("/economic", response_model=EconomicImpactResponse)
async def get_economic_impact(
    analysis_date: Optional[date] = Query(None, description="分析対象日"),
    include_calendar: bool = Query(True, description="経済カレンダーを含める"),
    days_ahead: int = Query(30, description="先読みする日数", ge=1, le=90),
    db: Session = Depends(get_db)
) -> EconomicImpactResponse:
    """
    経済指標の影響度分析を取得
    
    - **analysis_date**: 分析対象日
    - **include_calendar**: 経済カレンダー情報を含める
    - **days_ahead**: 今後何日先まで見るか
    - **returns**: 中央銀行政策、マクロ経済トレンド、市場センチメント等の総合分析
    """
    
    try:
        service = IndicatorsService(db)
        return await service.get_economic_impact(analysis_date, include_calendar, days_ahead)
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"経済指標分析の取得中にエラーが発生しました: {str(e)}"
        )


# ===================================================================
# 指標サマリーエンドポイント
# ===================================================================

@router.get("/summary")
async def get_indicators_summary(db: Session = Depends(get_db)):
    """テクニカル・経済指標の総合サマリーを取得"""
    try:
        return {
            "technical_signal": "BUY",
            "economic_sentiment": "BULLISH",
            "overall_recommendation": "CAUTIOUS_BUY",
            "confidence_level": 0.72,
            "key_factors": [
                "FED政策支持",
                "テクニカル的上昇トレンド",
                "適度なボラティリティ環境"
            ],
            "risk_factors": [
                "地政学的不確実性",
                "市場流動性リスク"
            ],
            "last_updated": datetime.now()
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"指標サマリーの取得中にエラーが発生しました: {str(e)}"
        )


# ===================================================================
# ヘルスチェック
# ===================================================================

@router.get("/health")
async def indicators_health_check():
    """指標APIのヘルスチェック"""
    return {
        "status": "healthy",
        "service": "indicators",
        "timestamp": datetime.now(),
        "version": "1.0.0"
    }