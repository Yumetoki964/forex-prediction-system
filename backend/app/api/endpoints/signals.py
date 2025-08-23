"""
Forex Prediction System - Trading Signals Endpoints
==================================================

売買シグナル関連のFastAPIエンドポイント
エンドポイント1.3: /api/signals/current (GET) - 現在の売買シグナル取得
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime, date
from decimal import Decimal

from ...database import get_db
from ...schemas.signals import (
    CurrentSignalResponse, 
    TradingSignalResponse,
    TradingSignalCreate
)
from ...models import TradingSignal, SignalType
from ...services.signals_service import SignalsService

router = APIRouter()


@router.get("/current", response_model=CurrentSignalResponse)
async def get_current_signal(db: AsyncSession = Depends(get_db)):
    """
    現在の売買シグナル取得エンドポイント
    
    5段階の売買判定（強い売り〜強い買い）を信頼度・強度付きで返却
    前回シグナルからの変化とUI表示用の情報も含む
    """
    try:
        service = SignalsService(db)
        return await service.get_current_signal()
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"売買シグナル取得に失敗しました: {str(e)}"
        )

