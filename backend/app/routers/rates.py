"""
Forex Prediction System - Rates API Router
==========================================

現在レートと為替レート関連のFastAPIルーター
エンドポイント 1.1: /api/rates/current 実装
"""

from datetime import datetime, timedelta
from typing import Optional
from fastapi import APIRouter, HTTPException, status, Query, Depends
from sqlalchemy.orm import Session

from ..schemas.rates_minimal import CurrentRateResponse
from ..services.rates_service import RatesService
from ..database import get_db

router = APIRouter()


@router.get("/current", response_model=CurrentRateResponse)
async def get_current_rate(db: Session = Depends(get_db)) -> CurrentRateResponse:
    """
    現在のドル円レートを取得
    
    エンドポイント: GET /api/rates/current
    
    Returns:
        CurrentRateResponse: 現在レート情報（変動率、OHLC、市場状況を含む）
    """
    try:
        service = RatesService(db)
        return await service.get_current_rate()
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get current rate: {str(e)}"
        )


# 他のエンドポイントは一時的にコメントアウト（Pydanticの問題解決後に復旧）
# @router.get("/history")
# @router.get("/statistics")


def _is_market_open(current_time: datetime) -> bool:
    """
    為替市場の開場状況を判定（仮実装）
    
    Args:
        current_time: 現在時刻
    
    Returns:
        bool: 市場開場中かどうか
    """
    # 仮実装：平日9:00-17:00を開場時間とする
    weekday = current_time.weekday()  # 0=月曜, 6=日曜
    hour = current_time.hour
    
    # 土日は閉場
    if weekday >= 5:  # 土日
        return False
    
    # 平日9-17時を開場時間とする（実際の為替市場は24時間）
    return 9 <= hour < 17


@router.get("/health")
async def rates_health_check():
    """
    Rates APIのヘルスチェック
    
    Returns:
        dict: ヘルスチェック結果
    """
    return {
        "status": "healthy",
        "service": "rates-api",
        "timestamp": datetime.now(),
        "version": "1.0.0"
    }