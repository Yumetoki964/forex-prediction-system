"""
アラート管理エンドポイント
"""
from fastapi import APIRouter, HTTPException
from typing import List, Optional
from datetime import datetime
from pydantic import BaseModel

router = APIRouter()

class Alert(BaseModel):
    id: int
    type: str  # 'price', 'signal', 'news'
    severity: str  # 'info', 'warning', 'critical'
    message: str
    timestamp: datetime
    is_read: bool = False
    currency_pair: str

class AlertResponse(BaseModel):
    alerts: List[Alert]
    unread_count: int
    total_count: int

@router.get("/active", response_model=AlertResponse)
async def get_active_alerts():
    """アクティブなアラートを取得"""
    # デモデータ
    alerts = [
        Alert(
            id=1,
            type="price",
            severity="warning",
            message="USD/JPY が設定した閾値（150.00）を超えました",
            timestamp=datetime.now(),
            is_read=False,
            currency_pair="USDJPY"
        ),
        Alert(
            id=2,
            type="signal",
            severity="info",
            message="EUR/USD で買いシグナルが検出されました",
            timestamp=datetime.now(),
            is_read=False,
            currency_pair="EURUSD"
        ),
        Alert(
            id=3,
            type="news",
            severity="critical",
            message="重要な経済指標発表: 米国雇用統計",
            timestamp=datetime.now(),
            is_read=False,
            currency_pair="USDJPY"
        )
    ]
    
    return AlertResponse(
        alerts=alerts,
        unread_count=3,
        total_count=3
    )

@router.post("/{alert_id}/read")
async def mark_alert_as_read(alert_id: int):
    """アラートを既読にする"""
    return {"message": f"Alert {alert_id} marked as read", "success": True}

@router.delete("/{alert_id}")
async def delete_alert(alert_id: int):
    """アラートを削除"""
    return {"message": f"Alert {alert_id} deleted", "success": True}

@router.get("/settings")
async def get_alert_settings():
    """アラート設定を取得"""
    return {
        "price_alerts_enabled": True,
        "signal_alerts_enabled": True,
        "news_alerts_enabled": True,
        "email_notifications": False,
        "push_notifications": True,
        "thresholds": {
            "USDJPY": {"upper": 152.0, "lower": 148.0},
            "EURUSD": {"upper": 1.10, "lower": 1.05}
        }
    }

@router.put("/settings")
async def update_alert_settings(settings: dict):
    """アラート設定を更新"""
    return {"message": "Alert settings updated", "settings": settings}