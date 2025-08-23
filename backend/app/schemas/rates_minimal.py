"""
Forex Prediction System - Minimal Rates API Schemas
================================================

最小限の現在レート用Pydanticスキーマ（テスト用）
"""

from datetime import datetime
from typing import Optional
from pydantic import BaseModel


class CurrentRateResponse(BaseModel):
    """現在レート取得レスポンス"""
    rate: float
    timestamp: datetime
    change_24h: float
    change_percentage_24h: float
    open_rate: Optional[float] = None
    high_rate: Optional[float] = None
    low_rate: Optional[float] = None
    volume: Optional[int] = None
    is_market_open: bool
    source: str