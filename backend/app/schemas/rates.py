"""
Forex Prediction System - Rates API Schemas
==========================================

現在レートと為替レート関連のPydanticスキーマ定義
エンドポイント 1.1: /api/rates/current 用のレスポンスモデル
"""

from datetime import datetime, date
from decimal import Decimal
from typing import Optional, List
from pydantic import BaseModel, Field


class CurrentRateResponse(BaseModel):
    """
    現在レート取得レスポンス
    エンドポイント: GET /api/rates/current
    """
    # 基本レート情報
    rate: float = Field(..., description="現在のドル円レート", example=150.25)
    timestamp: datetime = Field(..., description="レートの取得日時")
    
    # 変動情報
    change_24h: float = Field(..., description="24時間の変動額", example=1.25)
    change_percentage_24h: float = Field(..., description="24時間の変動率（%）", example=0.83)
    
    # OHLC情報（当日分）
    open_rate: Optional[float] = Field(None, description="本日始値", example=149.80)
    high_rate: Optional[float] = Field(None, description="本日高値", example=150.45)
    low_rate: Optional[float] = Field(None, description="本日安値", example=149.55)
    
    # 追加情報
    volume: Optional[int] = Field(None, description="出来高")
    is_market_open: bool = Field(..., description="市場開場状況", example=True)
    source: str = Field(..., description="データソース", example="yahoo_finance")
    
    class Config:
        from_attributes = True


class ExchangeRateItem(BaseModel):
    """
    為替レート単体アイテム（履歴データ用）
    """
    id: int = Field(..., description="レコードID")
    date: date = Field(..., description="レート日付")
    
    # OHLC データ
    open_rate: Optional[float] = Field(None, description="始値")
    high_rate: Optional[float] = Field(None, description="高値")
    low_rate: Optional[float] = Field(None, description="安値")
    close_rate: float = Field(..., description="終値（メインレート）")
    
    # 追加情報
    volume: Optional[int] = Field(None, description="出来高")
    source: str = Field(..., description="データソース")
    is_holiday: bool = Field(False, description="祝日フラグ")
    is_interpolated: bool = Field(False, description="補間データフラグ")
    
    # タイムスタンプ
    created_at: datetime = Field(..., description="作成日時")
    updated_at: datetime = Field(..., description="更新日時")
    
    class Config:
        from_attributes = True


class ExchangeRateListResponse(BaseModel):
    """
    為替レート一覧レスポンス（履歴データ用）
    """
    rates: List[ExchangeRateItem] = Field(..., description="レート一覧")
    total_count: int = Field(..., description="総件数")
    page: int = Field(1, description="ページ番号")
    per_page: int = Field(100, description="ページあたり件数")
    has_next: bool = Field(False, description="次ページ有無")
    has_prev: bool = Field(False, description="前ページ有無")


class RateStatistics(BaseModel):
    """
    レート統計情報
    """
    period_days: int = Field(..., description="統計期間（日数）", example=30)
    average_rate: float = Field(..., description="平均レート", example=150.12)
    max_rate: float = Field(..., description="最高値", example=152.80)
    min_rate: float = Field(..., description="最安値", example=148.25)
    volatility: float = Field(..., description="ボラティリティ", example=0.85)
    trend_direction: str = Field(..., description="トレンド方向", example="upward")  # upward, downward, sideways