"""
Historical Charts API Endpoints
===============================

Phase B-2aの対象エンドポイント:
- 2.1: /api/charts/historical (GET) - 履歴チャートデータ取得

仮実装でレスポンスを返し、後のサービス層実装で置き換え予定
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime, date, timedelta

from ...database import get_db
from ...schemas.charts import (
    HistoricalChartResponse,
    CandlestickData,
    MovingAverageData,
    RSIData,
    MACDData,
    BollingerBandsData,
    StochasticData,
    ATRData,
    SupportResistanceLevel,
    FibonacciLevel,
    TrendlineData,
    ChartAnnotation,
    ChartTimeframe,
    ChartPeriod,
    TechnicalIndicatorType,
    ChartQueryParams
)
from ...services.charts_service import ChartsService

router = APIRouter()


# ===================================================================
# 2.1: /api/charts/historical (GET) - 履歴チャートデータ取得
# ===================================================================

@router.get("/historical", response_model=HistoricalChartResponse)
async def get_historical_chart(
    period: ChartPeriod = Query(ChartPeriod.THREE_MONTHS, description="表示期間"),
    timeframe: ChartTimeframe = Query(ChartTimeframe.DAILY, description="時間軸"),
    indicators: List[TechnicalIndicatorType] = Query(default=[], description="表示するテクニカル指標"),
    include_volume: bool = Query(True, description="出来高を含める"),
    include_support_resistance: bool = Query(False, description="サポート・レジスタンスレベル"),
    include_fibonacci: bool = Query(False, description="フィボナッチレベル"),
    include_trendlines: bool = Query(False, description="トレンドライン"),
    db: Session = Depends(get_db)
) -> HistoricalChartResponse:
    """
    指定期間の為替チャートとテクニカル指標を取得
    
    - **period**: 表示期間（1week〜allまで）
    - **timeframe**: 時間軸（1m〜1Mまで）
    - **indicators**: 表示するテクニカル指標のリスト
    - **include_volume**: 出来高データを含める
    - **include_support_resistance**: サポート・レジスタンスレベルを含める
    - **include_fibonacci**: フィボナッチレベルを含める
    - **include_trendlines**: トレンドラインを含める
    - **returns**: 価格データとテクニカル指標の総合チャートデータ
    """
    
    try:
        service = ChartsService(db)
        return await service.get_historical_chart(
            period, timeframe, indicators, include_volume,
            include_support_resistance, include_fibonacci, include_trendlines
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"履歴チャートデータの取得中にエラーが発生しました: {str(e)}"
        )


# ===================================================================
# チャート設定エンドポイント
# ===================================================================

@router.get("/config/supported-indicators")
async def get_supported_indicators():
    """サポートされているテクニカル指標一覧を取得"""
    return {
        "indicators": [indicator.value for indicator in TechnicalIndicatorType],
        "timeframes": [timeframe.value for timeframe in ChartTimeframe],
        "periods": [period.value for period in ChartPeriod]
    }


@router.get("/config/default")
async def get_default_chart_config():
    """デフォルトのチャート設定を取得"""
    return {
        "period": ChartPeriod.THREE_MONTHS.value,
        "timeframe": ChartTimeframe.DAILY.value,
        "indicators": [
            TechnicalIndicatorType.SMA.value,
            TechnicalIndicatorType.RSI.value
        ],
        "include_volume": True,
        "include_support_resistance": False
    }


# ===================================================================
# ヘルスチェック
# ===================================================================

@router.get("/health")
async def charts_health_check():
    """チャートAPIのヘルスチェック"""
    return {
        "status": "healthy",
        "service": "charts",
        "timestamp": datetime.now(),
        "version": "1.0.0"
    }