"""
Predictions API Schema Definitions
==================================

Phase B-2aの対象エンドポイント用スキーマ:
- 1.2: /api/predictions/latest (GET) - 最新予測取得
- 2.2: /api/predictions/detailed (GET) - 詳細予測分析取得

SQLAlchemyモデルと整合性を保つPydanticスキーマを定義
"""

from pydantic import BaseModel, Field, ConfigDict
from typing import List, Optional, Dict, Any, Tuple
from datetime import datetime, date
from decimal import Decimal
from enum import Enum


class PredictionPeriod(str, Enum):
    """予測期間の列挙"""
    ONE_WEEK = "1week"
    TWO_WEEKS = "2weeks" 
    THREE_WEEKS = "3weeks"
    ONE_MONTH = "1month"


class PredictionModel(str, Enum):
    """予測モデルタイプの列挙"""
    LSTM = "lstm"
    XGBOOST = "xgboost"
    ENSEMBLE = "ensemble"


# ===================================================================
# 1.2: /api/predictions/latest (GET) - 最新予測取得
# ===================================================================

class PredictionItem(BaseModel):
    """個別の予測項目"""
    period: PredictionPeriod = Field(..., description="予測期間")
    predicted_rate: float = Field(..., description="予測レート", gt=0)
    confidence_interval_lower: Optional[float] = Field(None, description="信頼区間下限", gt=0)
    confidence_interval_upper: Optional[float] = Field(None, description="信頼区間上限", gt=0)
    confidence_level: float = Field(0.95, description="信頼水準", ge=0, le=1)
    volatility: Optional[float] = Field(None, description="ボラティリティ", ge=0)
    prediction_strength: float = Field(0.5, description="予測強度", ge=0, le=1)
    target_date: date = Field(..., description="予測対象日")

    model_config = ConfigDict(from_attributes=True, protected_namespaces=())


class LatestPredictionsResponse(BaseModel):
    """最新予測レスポンス"""
    predictions: List[PredictionItem] = Field(..., description="予測データ一覧")
    prediction_date: date = Field(..., description="予測実行日")
    confidence_level: float = Field(0.95, description="全体信頼水準", ge=0, le=1)
    generated_at: datetime = Field(..., description="生成日時")
    model_version: str = Field(..., description="使用モデルバージョン")
    
    model_config = ConfigDict(from_attributes=True, protected_namespaces=())


# ===================================================================
# 2.2: /api/predictions/detailed (GET) - 詳細予測分析取得
# ===================================================================

class FeatureImportance(BaseModel):
    """特徴量重要度"""
    feature_name: str = Field(..., description="特徴量名")
    importance_score: float = Field(..., description="重要度スコア", ge=0, le=1)
    category: str = Field(..., description="カテゴリ（technical/economic/temporal等）")

    model_config = ConfigDict(from_attributes=True, protected_namespaces=())


class ModelAnalysis(BaseModel):
    """モデル分析情報"""
    model_type: PredictionModel = Field(..., description="モデルタイプ")
    weight: float = Field(..., description="アンサンブル重み", ge=0, le=1)
    individual_prediction: float = Field(..., description="個別予測値", gt=0)
    confidence_score: float = Field(..., description="信頼度スコア", ge=0, le=1)
    feature_importance: List[FeatureImportance] = Field(default_factory=list, description="特徴量重要度")

    model_config = ConfigDict(from_attributes=True, protected_namespaces=())


class DetailedPredictionItem(BaseModel):
    """詳細予測項目"""
    period: PredictionPeriod = Field(..., description="予測期間")
    predicted_rate: float = Field(..., description="最終予測レート", gt=0)
    confidence_interval_lower: Optional[float] = Field(None, description="信頼区間下限", gt=0)
    confidence_interval_upper: Optional[float] = Field(None, description="信頼区間上限", gt=0)
    volatility: Optional[float] = Field(None, description="予測ボラティリティ", ge=0)
    prediction_strength: float = Field(0.5, description="予測強度", ge=0, le=1)
    target_date: date = Field(..., description="予測対象日")
    
    # 詳細分析情報
    model_analyses: List[ModelAnalysis] = Field(..., description="モデル別分析")
    uncertainty_factors: List[str] = Field(default_factory=list, description="不確実性要因")
    risk_assessment: str = Field("medium", description="リスク評価（low/medium/high/critical）")
    scenario_analysis: Optional[Dict[str, float]] = Field(None, description="シナリオ分析（楽観/悲観/現実的）")

    model_config = ConfigDict(from_attributes=True, protected_namespaces=())


class MarketCondition(BaseModel):
    """市場環境分析"""
    trend_direction: str = Field(..., description="トレンド方向（upward/downward/sideways）")
    trend_strength: float = Field(..., description="トレンド強度", ge=0, le=1)
    volatility_regime: str = Field(..., description="ボラティリティ環境（low/normal/high/extreme）")
    market_sentiment: str = Field(..., description="市場センチメント（bearish/neutral/bullish）")
    liquidity_condition: str = Field(..., description="流動性環境（tight/normal/abundant）")

    model_config = ConfigDict(from_attributes=True, protected_namespaces=())


class DetailedPredictionsResponse(BaseModel):
    """詳細予測分析レスポンス"""
    predictions: List[DetailedPredictionItem] = Field(..., description="詳細予測データ")
    prediction_date: date = Field(..., description="予測実行日")
    current_rate: float = Field(..., description="現在レート", gt=0)
    market_condition: MarketCondition = Field(..., description="市場環境分析")
    
    # メタデータ
    model_version: str = Field(..., description="使用モデルバージョン")
    data_quality_score: float = Field(1.0, description="データ品質スコア", ge=0, le=1)
    prediction_horizon_days: Dict[PredictionPeriod, int] = Field(..., description="期間別予測日数")
    generated_at: datetime = Field(..., description="生成日時")
    
    # 実行統計
    processing_time_seconds: Optional[float] = Field(None, description="処理時間（秒）", ge=0)
    data_points_used: Optional[int] = Field(None, description="使用データポイント数", ge=0)

    model_config = ConfigDict(from_attributes=True, protected_namespaces=())


# ===================================================================
# 共通ユーティリティスキーマ
# ===================================================================

class PredictionErrorResponse(BaseModel):
    """予測API共通エラーレスポンス"""
    error: str = Field(..., description="エラータイプ")
    message: str = Field(..., description="エラーメッセージ")
    details: Optional[Dict[str, Any]] = Field(None, description="エラー詳細")
    timestamp: datetime = Field(..., description="エラー発生時刻")

    model_config = ConfigDict(from_attributes=True, protected_namespaces=())


class PredictionHealthCheck(BaseModel):
    """予測システムヘルスチェック"""
    status: str = Field(..., description="システム状態（healthy/degraded/unhealthy）")
    last_prediction_time: Optional[datetime] = Field(None, description="最終予測実行時刻")
    model_status: Dict[str, str] = Field(..., description="モデル別状態")
    data_freshness_hours: float = Field(..., description="データ鮮度（時間）", ge=0)
    prediction_queue_length: int = Field(0, description="予測キューの長さ", ge=0)

    model_config = ConfigDict(from_attributes=True, protected_namespaces=())