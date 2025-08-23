"""
Test suite for SignalsService
============================

Phase S-3a: 売買シグナル生成とアラート機能のテスト
依存性注入による実データベーステスト（モック不使用）
"""

import pytest
from datetime import datetime, date, timedelta
from decimal import Decimal
from sqlalchemy.ext.asyncio import AsyncSession

from app.services.signals_service import SignalsService
from app.models import (
    TradingSignal, SignalType, ExchangeRate, Prediction, 
    TechnicalIndicator, PredictionPeriod, DataSourceType
)
from app.schemas.signals import TradingSignalCreate, CurrentSignalResponse


@pytest.mark.asyncio
async def test_signals_service_initialization(db_session: AsyncSession):
    """SignalsServiceの初期化テスト"""
    service = SignalsService(db_session)
    assert service.db == db_session


@pytest.mark.asyncio
async def test_get_current_signal_with_existing_data(db_session: AsyncSession):
    """既存シグナルがある場合の現在シグナル取得テスト"""
    service = SignalsService(db_session)
    
    # テスト用データを準備
    today = date.today()
    
    # 為替レートデータを作成
    test_rate = ExchangeRate(
        date=today,
        open_rate=Decimal("150.00"),
        high_rate=Decimal("151.00"),
        low_rate=Decimal("149.50"),
        close_rate=Decimal("150.45"),
        volume=1000000,
        source=DataSourceType.YAHOO_FINANCE
    )
    db_session.add(test_rate)
    
    # 既存シグナルを作成
    existing_signal = TradingSignal(
        date=today,
        signal_type=SignalType.BUY,
        confidence=0.75,
        strength=0.65,
        reasoning='{"test": true}',
        technical_score=0.6,
        prediction_score=0.7,
        current_rate=Decimal("150.45")
    )
    db_session.add(existing_signal)
    await db_session.commit()
    
    # テスト実行
    result = await service.get_current_signal()
    
    # 検証
    assert isinstance(result, CurrentSignalResponse)
    assert result.signal.signal_type == SignalType.BUY
    assert result.signal.confidence == 0.75
    assert result.display_text == "買いシグナル"
    assert result.color_code == "#4CAF50"
    assert result.last_updated is not None


@pytest.mark.asyncio
async def test_get_current_signal_auto_generation(db_session: AsyncSession):
    """シグナルが存在しない場合の自動生成テスト"""
    service = SignalsService(db_session)
    
    # テスト用為替レートを準備
    today = date.today()
    test_rate = ExchangeRate(
        date=today,
        open_rate=Decimal("149.00"),
        high_rate=Decimal("150.00"),
        low_rate=Decimal("148.50"),
        close_rate=Decimal("149.75"),
        volume=800000,
        source=DataSourceType.YAHOO_FINANCE
    )
    db_session.add(test_rate)
    
    # テクニカル指標データを準備
    test_indicator = TechnicalIndicator(
        date=today,
        exchange_rate_id=test_rate.id,
        rsi_14=Decimal("45.2"),
        macd=Decimal("0.5"),
        macd_signal=Decimal("0.3"),
        sma_5=Decimal("149.8"),
        sma_25=Decimal("149.2"),
        bb_upper=Decimal("151.0"),
        bb_middle=Decimal("149.5"),
        bb_lower=Decimal("148.0")
    )
    db_session.add(test_indicator)
    
    # 予測データを準備
    test_prediction = Prediction(
        prediction_date=today,
        target_date=today + timedelta(days=7),
        period=PredictionPeriod.ONE_WEEK,
        predicted_rate=Decimal("151.00"),
        confidence_interval_lower=Decimal("149.50"),
        confidence_interval_upper=Decimal("152.50"),
        confidence_level=0.95,
        volatility=0.15,
        prediction_strength=0.75,
        model_version="test_v1.0"
    )
    db_session.add(test_prediction)
    await db_session.commit()
    
    # シグナル生成前に確認（今日のシグナルは存在しない）
    existing_signal = await service.get_by_date(today)
    assert existing_signal is None
    
    # テスト実行
    result = await service.get_current_signal()
    
    # 検証
    assert isinstance(result, CurrentSignalResponse)
    assert result.signal.date == today
    assert result.signal.signal_type in [
        SignalType.STRONG_SELL, SignalType.SELL, SignalType.HOLD, 
        SignalType.BUY, SignalType.STRONG_BUY
    ]
    assert 0.0 <= result.signal.confidence <= 1.0
    assert 0.0 <= result.signal.strength <= 1.0
    assert result.signal.current_rate == Decimal("149.75")


@pytest.mark.asyncio
async def test_signal_crud_operations(db_session: AsyncSession):
    """シグナルCRUD操作のテスト"""
    service = SignalsService(db_session)
    
    # Create テスト
    signal_data = TradingSignalCreate(
        date=date.today(),
        signal_type=SignalType.SELL,
        confidence=0.82,
        strength=0.7,
        reasoning='{"test_create": true}',
        technical_score=0.6,
        prediction_score=0.8,
        current_rate=Decimal("148.90")
    )
    
    created_signal = await service.create(signal_data)
    assert created_signal.id is not None
    assert created_signal.signal_type == SignalType.SELL
    assert created_signal.confidence == 0.82
    
    # Read テスト
    retrieved_signal = await service.get_by_id(created_signal.id)
    assert retrieved_signal is not None
    assert retrieved_signal.signal_type == SignalType.SELL
    
    # Get by date テスト
    date_signal = await service.get_by_date(date.today())
    assert date_signal is not None
    assert date_signal.id == created_signal.id
    
    # Get all テスト
    all_signals = await service.get_all(limit=10)
    assert len(all_signals) >= 1
    assert any(s.id == created_signal.id for s in all_signals)


@pytest.mark.asyncio 
async def test_technical_score_calculation(db_session: AsyncSession):
    """テクニカル分析スコア計算のテスト"""
    service = SignalsService(db_session)
    
    # テクニカル指標データを準備（買いシグナル想定）
    today = date.today()
    test_rate = ExchangeRate(
        date=today,
        close_rate=Decimal("150.00"),
        source=DataSourceType.YAHOO_FINANCE
    )
    db_session.add(test_rate)
    
    # 買いシグナルを示すテクニカル指標
    test_indicator = TechnicalIndicator(
        date=today,
        exchange_rate_id=test_rate.id,
        rsi_14=Decimal("25.0"),         # 買われすぎ
        macd=Decimal("0.8"),           # 上昇トレンド
        macd_signal=Decimal("0.2"),    
        sma_5=Decimal("150.5"),        # 短期MA > 長期MA
        sma_25=Decimal("149.0"),
        bb_upper=Decimal("152.0"),
        bb_middle=Decimal("150.0"),
        bb_lower=Decimal("148.0")      # 下限近くで買いシグナル
    )
    db_session.add(test_indicator)
    await db_session.commit()
    
    # プライベートメソッドを直接テスト
    technical_score = await service._calculate_technical_score(today)
    
    # 買いシグナルなのでプラススコア
    assert 0.0 < technical_score <= 1.0


@pytest.mark.asyncio
async def test_prediction_score_calculation(db_session: AsyncSession):
    """予測分析スコア計算のテスト"""
    service = SignalsService(db_session)
    
    today = date.today()
    
    # 現在レートデータ
    current_rate = ExchangeRate(
        date=today,
        close_rate=Decimal("150.00"),
        source=DataSourceType.YAHOO_FINANCE
    )
    db_session.add(current_rate)
    
    # 上昇予測データ
    prediction = Prediction(
        prediction_date=today,
        target_date=today + timedelta(days=7),
        period=PredictionPeriod.ONE_WEEK,
        predicted_rate=Decimal("152.00"),  # 現在より2円高
        prediction_strength=0.8,
        model_version="test_v1.0"
    )
    db_session.add(prediction)
    await db_session.commit()
    
    # テスト実行
    score, prediction_id = await service._calculate_prediction_score(today)
    
    # 上昇予測なのでプラススコア
    assert score > 0.0
    assert prediction_id == prediction.id


@pytest.mark.asyncio
async def test_signal_display_helpers(db_session: AsyncSession):
    """シグナル表示ヘルパー関数のテスト"""
    service = SignalsService(db_session)
    
    # 各シグナルタイプのテスト
    test_cases = [
        (SignalType.STRONG_BUY, "強い買いシグナル", "#2E7D32", "↑↑"),
        (SignalType.BUY, "買いシグナル", "#4CAF50", "↑"),
        (SignalType.HOLD, "様子見", "#FF9800", "→"),
        (SignalType.SELL, "売りシグナル", "#F44336", "↓"),
        (SignalType.STRONG_SELL, "強い売りシグナル", "#D32F2F", "↓↓")
    ]
    
    for signal_type, expected_text, expected_color, expected_arrow in test_cases:
        # 表示テキストのテスト
        display_text = service._get_signal_display_text(signal_type)
        assert display_text == expected_text
        
        # 色のテスト
        color = service._get_signal_color(signal_type)
        assert color == expected_color
        
        # トレンド矢印のテスト（強度 > 0.7 の場合）
        arrow = service._get_trend_arrow(signal_type, 0.8)
        if signal_type in [SignalType.STRONG_BUY, SignalType.STRONG_SELL]:
            assert "↑↑" in arrow or "↓↓" in arrow
        elif signal_type == SignalType.HOLD:
            assert arrow == "→"


@pytest.mark.asyncio
async def test_integrated_signal_generation(db_session: AsyncSession):
    """統合シグナル生成のテスト"""
    service = SignalsService(db_session)
    
    # 様々なスコア組み合わせをテスト
    test_cases = [
        (0.8, 0.7, SignalType.STRONG_BUY),  # 強い買い
        (0.3, 0.4, SignalType.BUY),         # 買い
        (0.1, -0.1, SignalType.HOLD),       # 様子見
        (-0.4, -0.3, SignalType.SELL),      # 売り
        (-0.8, -0.7, SignalType.STRONG_SELL) # 強い売り
    ]
    
    for tech_score, pred_score, expected_signal in test_cases:
        signal_type, confidence, strength = service._generate_integrated_signal(
            tech_score, pred_score
        )
        
        assert signal_type == expected_signal
        assert 0.0 <= confidence <= 1.0
        assert 0.0 <= strength <= 1.0


@pytest.mark.asyncio
async def test_signal_change_detection(db_session: AsyncSession):
    """シグナル変化検出のテスト"""
    service = SignalsService(db_session)
    
    # 2日分のシグナルを作成
    yesterday = date.today() - timedelta(days=1)
    today = date.today()
    
    # 昨日のシグナル（HOLD）
    yesterday_signal = TradingSignal(
        date=yesterday,
        signal_type=SignalType.HOLD,
        confidence=0.5,
        strength=0.3,
        current_rate=Decimal("150.00")
    )
    db_session.add(yesterday_signal)
    
    # 今日のシグナル（BUY）
    today_signal = TradingSignal(
        date=today,
        signal_type=SignalType.BUY,
        confidence=0.7,
        strength=0.6,
        current_rate=Decimal("150.50")
    )
    db_session.add(today_signal)
    await db_session.commit()
    
    # 現在シグナル取得
    result = await service.get_current_signal()
    
    # シグナル変化が検出されることを確認
    assert result.signal_changed is True
    assert result.previous_signal == SignalType.HOLD
    assert result.signal.signal_type == SignalType.BUY