"""
Forex Prediction System - Alerts Endpoints
==========================================

アラート関連のFastAPIエンドポイント
エンドポイント1.5: /api/alerts/active (GET) - アクティブアラート取得
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime
from typing import List

from ...database import get_db
from ...schemas.alerts import (
    ActiveAlertsResponse,
    ActiveAlertResponse,
    AlertSeverityInfo,
    AlertAcknowledgeRequest
)
from ...models import ActiveAlert, AlertType
from ...services.alerts_service import AlertsService

router = APIRouter()


@router.get("/active", response_model=ActiveAlertsResponse)
async def get_active_alerts(db: AsyncSession = Depends(get_db)):
    """
    アクティブアラート一覧取得エンドポイント
    
    現在発生中のアラートを重要度別に整理して返却
    ダッシュボード表示用のサマリー情報も含む
    """
    try:
        service = AlertsService(db)
        return await service.get_active_alerts()
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"アクティブアラート取得に失敗しました: {str(e)}"
        )


@router.post("/acknowledge")
async def acknowledge_alerts(
    request: AlertAcknowledgeRequest,
    db: AsyncSession = Depends(get_db)
):
    """
    アラート確認エンドポイント
    
    指定されたアラートを確認済みにマークする
    """
    try:
        service = AlertsService(db)
        return await service.acknowledge_alerts(request)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"アラート確認に失敗しました: {str(e)}"
        )

