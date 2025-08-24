"""
Settings API Router
==================

予測設定とアラート設定のAPIエンドポイントを定義
API契約フェーズA-1b担当エンドポイント: 5.1, 5.3 (完了済み)
API契約フェーズC-3c担当エンドポイント: 5.2, 5.4, 5.5 (本実装)
"""

from fastapi import APIRouter, HTTPException, status, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional
from datetime import datetime
from decimal import Decimal
import json

from ..database import get_db
from ..core.dependencies import get_current_active_user
from ..models import User
from ..schemas.settings import (
    PredictionSettingsResponse,
    PredictionSettingsUpdate,
    AlertSettingsResponse,
    AlertSettingsUpdate,
    UpdateResponse,
    TestResultResponse,
    SettingsErrorResponse,
    AlertCondition
)
from ..models import PredictionSetting, AlertSetting
from ..services.settings_service import SettingsService

router = APIRouter()

# ===================================================================
# 5.1: 予測設定取得 (GET /api/settings/prediction)
# ===================================================================

@router.get("/prediction", response_model=PredictionSettingsResponse)
async def get_prediction_settings(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
) -> PredictionSettingsResponse:
    """
    現在の予測設定を取得
    
    エンドポイント: GET /api/settings/prediction
    対応ページ: P-005 予測設定
    """
    try:
        service = SettingsService(db)
        return await service.get_prediction_settings()
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve prediction settings: {str(e)}"
        )


# ===================================================================
# 5.3: アラート設定取得 (GET /api/settings/alerts)
# ===================================================================

@router.get("/alerts", response_model=List[AlertSettingsResponse])
async def get_alert_settings(
    alert_type: Optional[str] = None,
    is_enabled: Optional[bool] = None,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
) -> List[AlertSettingsResponse]:
    """
    アラート設定を取得
    
    エンドポイント: GET /api/settings/alerts
    対応ページ: P-005 予測設定
    
    Args:
        alert_type: フィルター用アラートタイプ（オプション）
        is_enabled: 有効/無効でフィルター（オプション）
    """
    try:
        service = SettingsService(db)
        return await service.get_alert_settings(alert_type=alert_type, is_enabled=is_enabled)
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve alert settings: {str(e)}"
        )


# ===================================================================
# 5.2, 5.4, 5.5: 設定更新・テストエンドポイント（Phase C-3c実装）
# ===================================================================

@router.put("/prediction", response_model=UpdateResponse)
async def update_prediction_settings(
    settings: PredictionSettingsUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
) -> UpdateResponse:
    """
    予測設定を更新
    
    エンドポイント: PUT /api/settings/prediction
    対応ページ: P-005 予測設定
    """
    try:
        service = SettingsService(db)
        
        # Pydanticモデルを辞書に変換（Noneでない値のみ）
        settings_data = settings.dict(exclude_none=True, by_alias=True)
        
        # サービス層で更新実行
        updated_setting = await service.update_prediction_settings(settings_data)
        
        return UpdateResponse(
            success=True,
            message=f"Prediction settings '{updated_setting.name}' updated successfully",
            updated_at=updated_setting.updated_at
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update prediction settings: {str(e)}"
        )


@router.put("/alerts/{alert_id}", response_model=UpdateResponse)
async def update_alert_settings(
    alert_id: int,
    settings: AlertSettingsUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
) -> UpdateResponse:
    """
    アラート設定を更新
    
    エンドポイント: PUT /api/settings/alerts/{alert_id}
    対応ページ: P-005 予測設定
    """
    try:
        service = SettingsService(db)
        
        # Pydanticモデルを辞書に変換（Noneでない値のみ）
        settings_data = settings.dict(exclude_none=True)
        
        # サービス層で更新実行
        updated_setting = await service.update_alert_settings(alert_id, settings_data)
        
        return UpdateResponse(
            success=True,
            message=f"Alert setting '{updated_setting.name}' (ID: {alert_id}) updated successfully",
            updated_at=updated_setting.updated_at
        )
        
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update alert settings: {str(e)}"
        )


@router.post("/test", response_model=TestResultResponse)
async def test_prediction_settings(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
) -> TestResultResponse:
    """
    現在設定での予測テストを実行
    
    エンドポイント: POST /api/settings/test
    対応ページ: P-005 予測設定
    """
    try:
        service = SettingsService(db)
        
        # サービス層でテスト実行
        test_result = await service.test_prediction_settings()
        
        return TestResultResponse(**test_result)
        
    except Exception as e:
        # エラー時のレスポンス
        return TestResultResponse(
            success=False,
            test_prediction=None,
            confidence_interval=None,
            prediction_model_performance=None,
            execution_time_ms=0,
            message=f"Test execution failed: {str(e)}",
            tested_at=datetime.utcnow()
        )