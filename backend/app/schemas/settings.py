"""
Settings API Schemas
===================

予測設定とアラート設定のPydanticスキーマを定義
"""

from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, Dict, Any, List
from datetime import datetime
from decimal import Decimal


# ===================================================================
# 予測設定スキーマ（PredictionSetting対応）
# ===================================================================

class PredictionSettingsResponse(BaseModel):
    """
    予測設定取得レスポンス
    エンドポイント: GET /api/settings/prediction
    """
    model_config = ConfigDict(from_attributes=True, protected_namespaces=())
    
    id: int
    name: str
    is_active: bool
    
    # モデル設定
    prediction_model_weights: Dict[str, Any] = Field(description="JSONデコードされたモデル重み設定", alias="model_weights")
    
    # LSTM設定
    lstm_enabled: bool
    lstm_sequence_length: int = Field(ge=1, description="LSTM入力系列長（1以上）")
    lstm_layers: int = Field(ge=1, description="LSTM層数（1以上）")
    lstm_units: int = Field(ge=1, description="LSTMユニット数（1以上）")
    
    # XGBoost設定
    xgboost_enabled: bool
    xgboost_n_estimators: int = Field(ge=1, description="XGBoost推定器数（1以上）")
    xgboost_max_depth: int = Field(ge=1, description="XGBoost最大深度（1以上）")
    xgboost_learning_rate: Decimal = Field(gt=0, le=1, description="XGBoost学習率（0-1）")
    
    # アンサンブル設定
    ensemble_method: str = Field(description="統合方法（weighted_average等）")
    confidence_threshold: Decimal = Field(ge=0, le=1, description="信頼度閾値（0-1）")
    
    # 予測感度
    sensitivity_mode: str = Field(description="感度モード（conservative/standard/aggressive）")
    volatility_adjustment: bool = Field(description="ボラティリティ調整の有効/無効")
    
    # タイムスタンプ
    created_at: datetime
    updated_at: datetime


class PredictionSettingsUpdate(BaseModel):
    """
    予測設定更新リクエスト
    エンドポイント: PUT /api/settings/prediction
    """
    name: Optional[str] = None
    is_active: Optional[bool] = None
    
    # モデル設定
    prediction_model_weights: Optional[Dict[str, Any]] = Field(None, alias="model_weights")
    
    # LSTM設定
    lstm_enabled: Optional[bool] = None
    lstm_sequence_length: Optional[int] = Field(None, ge=1, description="LSTM入力系列長（1以上）")
    lstm_layers: Optional[int] = Field(None, ge=1, description="LSTM層数（1以上）")
    lstm_units: Optional[int] = Field(None, ge=1, description="LSTMユニット数（1以上）")
    
    # XGBoost設定
    xgboost_enabled: Optional[bool] = None
    xgboost_n_estimators: Optional[int] = Field(None, ge=1, description="XGBoost推定器数（1以上）")
    xgboost_max_depth: Optional[int] = Field(None, ge=1, description="XGBoost最大深度（1以上）")
    xgboost_learning_rate: Optional[Decimal] = Field(None, gt=0, le=1, description="XGBoost学習率（0-1）")
    
    # アンサンブル設定
    ensemble_method: Optional[str] = None
    confidence_threshold: Optional[Decimal] = Field(None, ge=0, le=1, description="信頼度閾値（0-1）")
    
    # 予測感度
    sensitivity_mode: Optional[str] = None
    volatility_adjustment: Optional[bool] = None


# ===================================================================
# アラート設定スキーマ（AlertSetting対応）
# ===================================================================

class AlertCondition(BaseModel):
    """
    アラート条件の詳細設定
    """
    threshold_rate: Optional[Decimal] = Field(None, gt=0, description="閾値レート（正数）")
    comparison_operator: Optional[str] = Field(None, description="比較演算子（gt/lt/eq/gte/lte）")
    confidence_threshold: Optional[Decimal] = Field(None, ge=0, le=1, description="信頼度閾値（0-1）")
    volatility_threshold: Optional[Decimal] = Field(None, ge=0, description="ボラティリティ閾値（0以上）")
    signal_types: Optional[List[str]] = Field(None, description="対象シグナルタイプ（strong_sell, sell等）")


class AlertSettingsResponse(BaseModel):
    """
    アラート設定取得レスポンス
    エンドポイント: GET /api/settings/alerts
    """
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    name: str = Field(description="アラート設定名")
    alert_type: str = Field(description="アラートタイプ（rate_threshold/signal_change/volatility_high/prediction_confidence_low）")
    
    # アラート条件
    is_enabled: bool = Field(description="アラートの有効/無効")
    conditions: AlertCondition = Field(description="JSONデコードされたアラート条件")
    
    # 通知設定
    email_enabled: bool = Field(description="メール通知の有効/無効")
    browser_notification_enabled: bool = Field(description="ブラウザ通知の有効/無効")
    email_address: Optional[str] = Field(None, description="通知先メールアドレス")
    
    # 実行制御
    cooldown_minutes: int = Field(ge=0, description="クールダウン期間（分、0以上）")
    max_alerts_per_day: int = Field(gt=0, description="1日最大アラート数（1以上）")
    
    # 統計情報
    triggered_count: int = Field(ge=0, description="発生回数（0以上）")
    last_triggered_at: Optional[datetime] = Field(None, description="最終発生日時")
    
    # タイムスタンプ
    created_at: datetime
    updated_at: datetime


class AlertSettingsUpdate(BaseModel):
    """
    アラート設定更新リクエスト
    エンドポイント: PUT /api/settings/alerts
    """
    name: Optional[str] = None
    alert_type: Optional[str] = None
    
    # アラート条件
    is_enabled: Optional[bool] = None
    conditions: Optional[AlertCondition] = None
    
    # 通知設定
    email_enabled: Optional[bool] = None
    browser_notification_enabled: Optional[bool] = None
    email_address: Optional[str] = None
    
    # 実行制御
    cooldown_minutes: Optional[int] = Field(None, ge=0, description="クールダウン期間（分、0以上）")
    max_alerts_per_day: Optional[int] = Field(None, gt=0, description="1日最大アラート数（1以上）")


# ===================================================================
# 共通レスポンススキーマ
# ===================================================================

class UpdateResponse(BaseModel):
    """
    設定更新時の共通レスポンス
    """
    success: bool = Field(description="更新成功フラグ")
    message: str = Field(description="更新結果メッセージ")
    updated_at: datetime = Field(description="更新実行日時")


class TestResultResponse(BaseModel):
    """
    予測設定テスト結果レスポンス
    エンドポイント: POST /api/settings/test
    """
    model_config = ConfigDict(protected_namespaces=())
    
    success: bool = Field(description="テスト実行成功フラグ")
    test_prediction: Optional[Decimal] = Field(None, gt=0, description="テスト予測値（正数）")
    confidence_interval: Optional[tuple[Decimal, Decimal]] = Field(None, description="信頼区間（下限、上限）")
    prediction_model_performance: Optional[Dict[str, Any]] = Field(None, description="モデルパフォーマンス指標", alias="model_performance")
    execution_time_ms: int = Field(ge=0, description="実行時間（ミリ秒、0以上）")
    message: str = Field(description="テスト結果メッセージ")
    tested_at: datetime = Field(description="テスト実行日時")


# ===================================================================
# エラーレスポンススキーマ
# ===================================================================

class SettingsErrorResponse(BaseModel):
    """
    設定関連のエラーレスポンス
    """
    error: str = Field(description="エラータイプ")
    message: str = Field(description="エラー詳細メッセージ")
    field: Optional[str] = Field(None, description="エラーが発生したフィールド名")
    timestamp: datetime = Field(description="エラー発生日時")