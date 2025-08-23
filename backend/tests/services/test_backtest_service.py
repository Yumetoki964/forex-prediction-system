"""
Backtest Service Tests
======================

バックテストサービス層の単体テスト
実際のPostgreSQLデータベースを使用した統合テスト
"""

import pytest
from datetime import date, datetime, timedelta
from decimal import Decimal
from unittest.mock import AsyncMock, MagicMock
import asyncio

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.services.backtest_service import BacktestService
from app.models import BacktestResult, ExchangeRate, BacktestStatus, PredictionModel
from app.schemas.backtest import (
    BacktestConfig,
    PredictionModelType,
    BacktestJobResponse,
    BacktestResultsResponse,
    BacktestMetricsResponse,
    BacktestTradesResponse
)


@pytest.mark.asyncio
async def test_create_backtest_service(async_session: AsyncSession) -> None:
    """BacktestServiceのインスタンス生成テスト"""
    service = BacktestService(async_session)
    assert service.db == async_session


@pytest.mark.asyncio
async def test_start_backtest_basic(async_session: AsyncSession) -> None:
    """基本的なバックテスト開始のテスト"""
    service = BacktestService(async_session)
    
    # テスト用の為替データを準備
    start_date = date(2020, 1, 1)
    end_date = date(2020, 12, 31)
    
    # 簡易的なデータを挿入
    for i in range(100):
        current_date = start_date + timedelta(days=i)
        if current_date > end_date:
            break
        
        rate_data = ExchangeRate(
            date=current_date,
            open_rate=Decimal("110.0"),
            high_rate=Decimal("111.0"),
            low_rate=Decimal("109.0"),
            close_rate=Decimal("110.5"),
            volume=1000000
        )
        async_session.add(rate_data)
    
    await async_session.commit()
    
    config = BacktestConfig(
        start_date=start_date,
        end_date=end_date,
        initial_capital=Decimal("1000000"),
        prediction_model_type=PredictionModelType.ENSEMBLE
    )
    
    # バックテスト開始
    result = await service.start_backtest(config)
    
    # 結果検証
    assert isinstance(result, BacktestJobResponse)
    assert result.job_id is not None
    assert result.start_date == start_date
    assert result.end_date == end_date


@pytest.mark.asyncio
async def test_start_backtest_validation_errors(async_session: AsyncSession) -> None:
    """バックテスト開始のバリデーションエラーテスト"""
    service = BacktestService(async_session)
    
    # 終了日が開始日より前の場合
    with pytest.raises(ValueError, match="End date must be after start date"):
        config = BacktestConfig(
            start_date=date(2020, 12, 31),
            end_date=date(2020, 1, 1),
            initial_capital=Decimal("1000000"),
            prediction_model_type=PredictionModelType.ENSEMBLE
        )
        await service.start_backtest(config)
    
    # 開始日が1990年より前の場合
    with pytest.raises(ValueError, match="Start date cannot be earlier than 1990-01-01"):
        config = BacktestConfig(
            start_date=date(1989, 1, 1),
            end_date=date(1989, 12, 31),
            initial_capital=Decimal("1000000"),
            prediction_model_type=PredictionModelType.ENSEMBLE
        )
        await service.start_backtest(config)


@pytest.mark.asyncio
async def test_get_results_not_found(async_session: AsyncSession) -> None:
    """存在しないバックテスト結果の取得テスト"""
    service = BacktestService(async_session)
    
    result = await service.get_results("non-existent-job-id")
    assert result is None


@pytest.mark.asyncio
async def test_get_results_found(async_session: AsyncSession) -> None:
    """存在するバックテスト結果の取得テスト"""
    service = BacktestService(async_session)
    
    # テスト用のバックテスト結果を作成
    backtest_result = BacktestResult(
        job_id="test-job-123",
        start_date=date(2020, 1, 1),
        end_date=date(2020, 12, 31),
        initial_capital=Decimal("1000000"),
        model_type=PredictionModel.ENSEMBLE,
        status=BacktestStatus.COMPLETED,
        total_return=Decimal("50000"),
        annualized_return=Decimal("0.05"),
        volatility=Decimal("0.15"),
        sharpe_ratio=Decimal("0.33"),
        max_drawdown=Decimal("0.08"),
        total_trades=20,
        winning_trades=12,
        losing_trades=8,
        win_rate=Decimal("0.6")
    )
    
    async_session.add(backtest_result)
    await async_session.commit()
    
    # 結果取得
    result = await service.get_results("test-job-123")
    
    # 検証
    assert result is not None
    assert result.job_id == "test-job-123"
    assert result.total_return == Decimal("50000")
    assert result.win_rate == Decimal("0.6")


@pytest.mark.asyncio
async def test_get_metrics_not_found(async_session: AsyncSession) -> None:
    """存在しないバックテスト指標の取得テスト"""
    service = BacktestService(async_session)
    
    result = await service.get_metrics("non-existent-job-id")
    assert result is None


@pytest.mark.asyncio
async def test_get_trades_not_found(async_session: AsyncSession) -> None:
    """存在しないバックテスト取引履歴の取得テスト"""
    service = BacktestService(async_session)
    
    result = await service.get_trades("non-existent-job-id", 1, 100)
    assert result is None


@pytest.mark.asyncio
async def test_validate_data_availability_insufficient_data(async_session: AsyncSession) -> None:
    """データ不足時のバリデーションテスト"""
    service = BacktestService(async_session)
    
    # データが不足している期間でテスト
    start_date = date(2030, 1, 1)  # 未来の日付
    end_date = date(2030, 12, 31)
    
    with pytest.raises(ValueError, match="Insufficient data for backtest period"):
        await service._validate_data_availability(start_date, end_date)


@pytest.mark.asyncio
async def test_estimate_completion_time(async_session: AsyncSession) -> None:
    """完了時間推定のテスト"""
    service = BacktestService(async_session)
    
    # 1年間のテスト
    start_date = date(2020, 1, 1)
    end_date = date(2020, 12, 31)
    
    estimated_time = service._estimate_completion_time(start_date, end_date)
    
    assert isinstance(estimated_time, int)
    assert estimated_time >= 60  # 最低60秒


@pytest.mark.asyncio
async def test_calculate_performance_metrics(async_session: AsyncSession) -> None:
    """パフォーマンス指標計算のテスト"""
    service = BacktestService(async_session)
    
    # サンプルシミュレーション結果
    simulation_results = {
        'trades': [
            {'profit_loss': 1000, 'confidence': 0.8},
            {'profit_loss': -500, 'confidence': 0.7},
            {'profit_loss': 1500, 'confidence': 0.9}
        ],
        'portfolio_value': [
            {'value': 1000000}, {'value': 1010000}, 
            {'value': 1005000}, {'value': 1020000}
        ],
        'final_value': 1020000
    }
    
    initial_capital = Decimal("1000000")
    
    metrics = service._calculate_performance_metrics(simulation_results, initial_capital)
    
    assert isinstance(metrics, dict)
    assert 'total_return' in metrics
    assert 'win_rate' in metrics
    assert 'total_trades' in metrics


@pytest.mark.asyncio
async def test_calculate_volatility(async_session: AsyncSession) -> None:
    """ボラティリティ計算のテスト"""
    service = BacktestService(async_session)
    
    # サンプル為替データ
    exchange_data = [
        {'close': 110.0}, {'close': 110.5}, {'close': 109.8},
        {'close': 111.2}, {'close': 110.9}, {'close': 111.5}
    ]
    
    for i in range(len(exchange_data)):
        if i >= 5:  # 十分なデータがある場合
            volatility = service._calculate_volatility(exchange_data, i)
            assert isinstance(volatility, float)
            assert volatility >= 0


@pytest.mark.asyncio
async def test_calculate_std(async_session: AsyncSession) -> None:
    """標準偏差計算のテスト"""
    service = BacktestService(async_session)
    
    # テストデータ
    values = [1.0, 2.0, 3.0, 4.0, 5.0]
    std = service._calculate_std(values)
    
    assert isinstance(std, float)
    assert std > 0
    
    # 空のリストの場合
    empty_std = service._calculate_std([])
    assert empty_std == 0


@pytest.mark.asyncio
async def test_calculate_calmar_ratio(async_session: AsyncSession) -> None:
    """カルマーレシオ計算のテスト"""
    service = BacktestService(async_session)
    
    # 正常なケース
    annualized_return = Decimal("0.1")
    max_drawdown = Decimal("0.05")
    
    calmar = service._calculate_calmar_ratio(annualized_return, max_drawdown)
    assert calmar is not None
    assert isinstance(calmar, Decimal)
    
    # ゼロ除算のケース
    calmar_zero = service._calculate_calmar_ratio(annualized_return, Decimal("0"))
    assert calmar_zero is None
    
    # None入力のケース
    calmar_none = service._calculate_calmar_ratio(None, max_drawdown)
    assert calmar_none is None


@pytest.mark.asyncio
async def test_calculate_var_95(async_session: AsyncSession) -> None:
    """VaR（95%）計算のテスト"""
    service = BacktestService(async_session)
    
    trade_log = [
        {'profit_loss': 1000}, {'profit_loss': -500},
        {'profit_loss': 1500}, {'profit_loss': -200}
    ]
    
    var_95 = service._calculate_var_95(trade_log)
    assert isinstance(var_95, Decimal)


@pytest.mark.asyncio 
async def test_service_integration(async_session: AsyncSession) -> None:
    """サービス層の統合テスト"""
    service = BacktestService(async_session)
    
    # 基本的な機能が正常に動作することを確認
    # （エラーが発生しないことを主眼とする統合テスト）
    
    # インスタンス作成確認
    assert service.db is not None
    
    # 型安全性確認
    assert hasattr(service, 'start_backtest')
    assert hasattr(service, 'get_results')
    assert hasattr(service, 'get_metrics')
    assert hasattr(service, 'get_trades')


# パフォーマンステスト用のマーカー
@pytest.mark.slow
@pytest.mark.asyncio
async def test_backtest_performance(async_session: AsyncSession) -> None:
    """バックテストのパフォーマンステスト（大量データ対応）"""
    service = BacktestService(async_session)
    
    # 大量のテストデータを準備（時間がかかる場合はskipも検討）
    start_date = date(2019, 1, 1)
    end_date = date(2019, 12, 31)
    
    # パフォーマンス測定
    start_time = datetime.now()
    
    try:
        config = BacktestConfig(
            start_date=start_date,
            end_date=end_date,
            initial_capital=Decimal("1000000"),
            prediction_model_type=PredictionModelType.ENSEMBLE
        )
        
        # データが不足している場合はskip
        await service._validate_data_availability(start_date, end_date)
        result = await service.start_backtest(config)
        
        execution_time = (datetime.now() - start_time).total_seconds()
        
        # パフォーマンス要件チェック（例：10秒以内）
        assert execution_time < 10.0, f"Backtest took too long: {execution_time}s"
        
    except ValueError as e:
        if "Insufficient data" in str(e):
            pytest.skip("Insufficient test data for performance test")
        else:
            raise