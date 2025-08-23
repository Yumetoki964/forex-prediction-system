"""
Forex Prediction System - Alerts Schemas
=======================================

アラート関連のPydanticスキーマ定義
アクティブアラートの表示とアラート設定管理
"""

from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, List
from datetime import datetime
from decimal import Decimal

from ..models import AlertType


class ActiveAlertResponse(BaseModel):
    """アクティブアラートレスポンスモデル"""
    
    # 基本情報
    id: int
    alert_setting_id: int
    
    # アラート内容
    title: str = Field(..., max_length=200, description="アラートタイトル")
    message: str = Field(..., description="アラートメッセージ")
    severity: str = Field(..., description="重要度（low, medium, high, critical）")
    
    # 状態管理
    is_acknowledged: bool = Field(False, description="確認済みフラグ")
    acknowledged_at: Optional[datetime] = Field(None, description="確認日時")
    
    # 関連データ
    exchange_rate_id: Optional[int] = Field(None, description="関連為替レートID")
    prediction_id: Optional[int] = Field(None, description="関連予測ID")
    
    # UI表示用追加情報
    icon: str = Field(..., description="アイコン種別")
    color_code: str = Field(..., description="UIカラーコード")
    urgency_level: int = Field(..., ge=1, le=5, description="緊急度レベル（1-5）")
    
    # タイムスタンプ
    created_at: datetime
    
    model_config = ConfigDict(from_attributes=True)


class AlertSettingInfo(BaseModel):
    """アラート設定情報（読み取り専用）"""
    
    id: int
    name: str
    alert_type: AlertType
    is_enabled: bool
    
    # 通知設定（最小限）
    email_enabled: bool
    browser_notification_enabled: bool
    cooldown_minutes: int
    
    model_config = ConfigDict(from_attributes=True)


class ActiveAlertsResponse(BaseModel):
    """アクティブアラート一覧取得APIレスポンス"""
    
    # アラート一覧
    alerts: List[ActiveAlertResponse] = Field(..., description="アクティブアラート一覧")
    
    # サマリー情報
    total_alerts: int = Field(..., description="総アラート数")
    unacknowledged_count: int = Field(..., description="未確認アラート数")
    critical_count: int = Field(..., description="緊急アラート数")
    
    # 優先度別カウント
    counts_by_severity: dict[str, int] = Field(..., description="重要度別カウント")
    
    # 最新アラート時刻
    latest_alert_at: Optional[datetime] = Field(None, description="最新アラート発生時刻")
    
    # UI表示制御
    show_notification_badge: bool = Field(False, description="通知バッジ表示フラグ")
    requires_attention: bool = Field(False, description="注意喚起フラグ")
    
    # メタデータ
    last_updated: datetime = Field(..., description="最終更新時刻")


class AlertAcknowledgeRequest(BaseModel):
    """アラート確認リクエスト（将来の機能用）"""
    
    alert_ids: List[int] = Field(..., description="確認するアラートID一覧")
    acknowledged_by: Optional[str] = Field(None, description="確認者情報")


class AlertSeverityInfo(BaseModel):
    """重要度情報定義"""
    
    level: str = Field(..., description="重要度レベル")
    display_name: str = Field(..., description="表示名")
    color: str = Field(..., description="カラーコード")
    icon: str = Field(..., description="アイコン名")
    urgency: int = Field(..., ge=1, le=5, description="緊急度")
    
    @classmethod
    def get_severity_info(cls, severity: str) -> "AlertSeverityInfo":
        """重要度情報を取得"""
        severity_map = {
            "low": cls(level="low", display_name="軽微", color="#4CAF50", icon="info", urgency=1),
            "medium": cls(level="medium", display_name="注意", color="#FF9800", icon="warning", urgency=2), 
            "high": cls(level="high", display_name="重要", color="#F44336", icon="priority_high", urgency=4),
            "critical": cls(level="critical", display_name="緊急", color="#D32F2F", icon="error", urgency=5)
        }
        return severity_map.get(severity, severity_map["medium"])