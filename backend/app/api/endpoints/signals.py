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
    # TODO: データベース実装後に以下のコメントを外す
    # try:
    #     service = SignalsService(db)
    #     return await service.get_current_signal()
    # except Exception as e:
    #     raise HTTPException(
    #         status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
    #         detail=f"売買シグナル取得に失敗しました: {str(e)}"
    #     )
    
    # モックデータを返す（データベース実装までの暫定処理）
    from datetime import datetime, timedelta
    import random
    import json
    
    signal_types = ["strong_buy", "buy", "hold", "sell", "strong_sell"]
    current_signal = random.choice(signal_types)
    
    signal_display = {
        "strong_buy": ("強い買い", "#00d4ff", "↑↑"),
        "buy": ("買い", "#00a0e9", "↑"),
        "hold": ("中立", "#ffc107", "→"),
        "sell": ("売り", "#ff9800", "↓"),
        "strong_sell": ("強い売り", "#f44336", "↓↓")
    }
    
    display_text, color_code, trend_arrow = signal_display[current_signal]
    
    # TradingSignalResponseオブジェクトを作成
    mock_signal = TradingSignalResponse(
        id=1,
        date=date.today(),
        signal_type=current_signal,
        confidence=random.uniform(0.6, 0.95),  # 0-1の範囲に修正
        strength=random.uniform(0.3, 0.9),
        reasoning=json.dumps({
            "technical": "RSI: 45, MACD: 買いシグナル",
            "prediction": "上昇トレンド予測",
            "market": "リスクオン相場"
        }),
        technical_score=random.uniform(-1, 1),
        prediction_score=random.uniform(-1, 1),
        prediction_id=None,
        current_rate=Decimal("150.25"),
        created_at=datetime.now()
    )
    
    return CurrentSignalResponse(
        signal=mock_signal,
        previous_signal="hold",
        signal_changed=current_signal != "hold",
        display_text=display_text,
        color_code=color_code,
        trend_arrow=trend_arrow,
        last_updated=datetime.now(),
        next_update_at=datetime.now() + timedelta(minutes=30)
    )

