"""
Forex Prediction System - Trading Signals Schemas
================================================

売買シグナル関連のPydanticスキーマ定義
5段階シグナル（強い売り〜強い買い）のレスポンスモデル
"""

from pydantic import BaseModel, Field, ConfigDict
from typing import Optional
from datetime import date, datetime
from decimal import Decimal

from ..models import SignalType


class TradingSignalResponse(BaseModel):
    """売買シグナルレスポンスモデル"""
    
    # 基本情報
    id: int
    date: date
    
    # シグナル情報  
    signal_type: SignalType = Field(..., description="売買シグナル種別")
    confidence: float = Field(..., ge=0, le=1, description="シグナル信頼度（0-1）")
    strength: float = Field(..., ge=0, le=1, description="シグナル強度（0-1）")
    
    # 根拠情報
    reasoning: Optional[str] = Field(None, description="シグナル根拠（JSON形式）")
    technical_score: Optional[float] = Field(None, description="テクニカル分析スコア")
    prediction_score: Optional[float] = Field(None, description="予測分析スコア")
    
    # 関連データ
    prediction_id: Optional[int] = Field(None, description="関連予測ID")
    current_rate: Decimal = Field(..., description="現在レート")
    
    # タイムスタンプ
    created_at: datetime
    
    model_config = ConfigDict(from_attributes=True)


class CurrentSignalResponse(BaseModel):
    """現在の売買シグナル取得APIレスポンス"""
    
    # 現在のシグナル
    signal: TradingSignalResponse
    
    # 前回シグナルからの変化
    previous_signal: Optional[SignalType] = Field(None, description="前回シグナル")
    signal_changed: bool = Field(False, description="シグナル変化フラグ")
    
    # UI表示用の追加情報
    display_text: str = Field(..., description="シグナル表示テキスト")
    color_code: str = Field(..., description="UIカラーコード")
    trend_arrow: str = Field(..., description="トレンド矢印表示")
    
    # メタデータ
    last_updated: datetime = Field(..., description="最終更新時刻")
    next_update_at: Optional[datetime] = Field(None, description="次回更新予定時刻")


class TradingSignalCreate(BaseModel):
    """売買シグナル作成用モデル（管理用）"""
    
    date: date
    signal_type: SignalType
    confidence: float = Field(..., ge=0, le=1)
    strength: float = Field(..., ge=0, le=1)
    reasoning: Optional[str] = None
    technical_score: Optional[float] = None
    prediction_score: Optional[float] = None
    prediction_id: Optional[int] = None
    current_rate: Decimal