"""
Test suite for AlertsService
============================

Phase S-3a: アラート生成と管理機能のテスト
依存性注入による実データベーステスト（モック不使用）
"""

import pytest
from datetime import datetime, date, timedelta
from decimal import Decimal
from sqlalchemy.ext.asyncio import AsyncSession

from app.services.alerts_service import AlertsService
from app.models import (
    ActiveAlert, AlertSetting, AlertType, ExchangeRate, 
    Prediction, TradingSignal, SignalType, PredictionPeriod, DataSourceType
)
from app.schemas.alerts import (
    ActiveAlertsResponse, ActiveAlertResponse, AlertAcknowledgeRequest
)


@pytest.mark.asyncio
async def test_alerts_service_initialization(db_session: AsyncSession):
    """AlertsServiceの初期化テスト"""
    service = AlertsService(db_session)
    assert service.db == db_session


@pytest.mark.asyncio
async def test_get_active_alerts_empty_database(db_session: AsyncSession):
    """空のデータベースでアクティブアラート取得テスト"""
    service = AlertsService(db_session)
    
    result = await service.get_active_alerts()
    
    # 検証
    assert isinstance(result, ActiveAlertsResponse)
    assert result.total_alerts == 0
    assert result.unacknowledged_count == 0
    assert result.critical_count == 0
    assert len(result.alerts) == 0
    assert result.latest_alert_at is None
    assert result.show_notification_badge is False


@pytest.mark.asyncio
async def test_create_and_get_active_alerts(db_session: AsyncSession):
    """アラート作成と取得のテスト"""
    service = AlertsService(db_session)
    
    # アラート設定を作成
    alert_setting = AlertSetting(
        name="テスト設定",
        alert_type=AlertType.RATE_THRESHOLD,
        is_enabled=True,
        conditions='{"threshold": 1.5}',
        email_enabled=False,
        browser_notification_enabled=True
    )
    db_session.add(alert_setting)
    await db_session.commit()
    
    # アクティブアラートを作成
    test_alert = await service._create_alert(
        title="テストアラート",
        message="これはテスト用のアラートです",
        severity="medium",
        alert_setting_id=alert_setting.id,
        icon="test_icon"
    )
    
    # アクティブアラートを取得
    result = await service.get_active_alerts()
    
    # 検証
    assert result.total_alerts == 1
    assert result.unacknowledged_count == 1
    assert len(result.alerts) == 1
    
    alert_response = result.alerts[0]
    assert alert_response.title == "テストアラート"
    assert alert_response.severity == "medium"
    assert alert_response.is_acknowledged is False


@pytest.mark.asyncio
async def test_acknowledge_alerts(db_session: AsyncSession):
    """アラート確認機能のテスト"""
    service = AlertsService(db_session)
    
    # アラート設定を準備
    alert_setting = AlertSetting(
        name="確認テスト設定",
        alert_type=AlertType.SIGNAL_CHANGE,
        is_enabled=True,
        conditions='{"signal_change": true}',
        email_enabled=False,
        browser_notification_enabled=True
    )
    db_session.add(alert_setting)
    await db_session.commit()
    
    # 2つのアラートを作成
    alert1 = await service._create_alert(
        title="アラート1",
        message="確認テスト用アラート1",
        severity="high",
        alert_setting_id=alert_setting.id
    )
    
    alert2 = await service._create_alert(
        title="アラート2", 
        message="確認テスト用アラート2",
        severity="medium",
        alert_setting_id=alert_setting.id
    )
    
    # 確認前の状態確認
    result_before = await service.get_active_alerts()
    assert result_before.unacknowledged_count == 2
    
    # アラートを確認
    acknowledge_request = AlertAcknowledgeRequest(
        alert_ids=[alert1.id, alert2.id],
        acknowledged_by="test_user"
    )
    
    acknowledge_result = await service.acknowledge_alerts(acknowledge_request)
    
    # 確認結果の検証
    assert acknowledge_result["acknowledged_count"] == 2
    assert alert1.id in acknowledge_result["acknowledged_ids"]
    assert alert2.id in acknowledge_result["acknowledged_ids"]
    
    # 確認後の状態確認
    result_after = await service.get_active_alerts()
    assert result_after.unacknowledged_count == 0
    assert all(alert.is_acknowledged for alert in result_after.alerts)


@pytest.mark.asyncio
async def test_rate_volatility_alert_generation(db_session: AsyncSession):
    """レート急変動アラート生成テスト"""
    service = AlertsService(db_session)
    
    today = date.today()
    yesterday = today - timedelta(days=1)
    
    # 昨日のレート
    yesterday_rate = ExchangeRate(
        date=yesterday,
        close_rate=Decimal("150.00"),
        source=DataSourceType.YAHOO_FINANCE
    )
    db_session.add(yesterday_rate)
    
    # 今日のレート（2%上昇）
    today_rate = ExchangeRate(
        date=today,
        close_rate=Decimal("153.00"),  # 2%上昇
        source=DataSourceType.YAHOO_FINANCE
    )
    db_session.add(today_rate)
    await db_session.commit()
    
    # 急変動アラートチェックを実行
    await service._check_rate_volatility_alerts()
    
    # アラートが生成されたか確認
    result = await service.get_active_alerts()
    
    volatility_alerts = [
        alert for alert in result.alerts 
        if "急変動" in alert.title
    ]
    
    assert len(volatility_alerts) >= 1
    volatility_alert = volatility_alerts[0]
    assert volatility_alert.severity in ["medium", "high"]
    assert "上昇" in volatility_alert.message


@pytest.mark.asyncio
async def test_signal_change_alert_generation(db_session: AsyncSession):
    """シグナル変更アラート生成テスト"""
    service = AlertsService(db_session)
    
    today = date.today()
    yesterday = today - timedelta(days=1)
    
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
    
    # シグナル変更アラートチェックを実行
    await service._check_signal_change_alerts()
    
    # アラートが生成されたか確認
    result = await service.get_active_alerts()
    
    signal_alerts = [
        alert for alert in result.alerts 
        if "シグナル変更" in alert.title
    ]
    
    assert len(signal_alerts) >= 1
    signal_alert = signal_alerts[0]
    assert signal_alert.severity == "medium"
    assert "買いシグナル" in signal_alert.message


@pytest.mark.asyncio
async def test_prediction_confidence_alert_generation(db_session: AsyncSession):
    """予測信頼度低下アラート生成テスト"""
    service = AlertsService(db_session)
    
    today = date.today()
    
    # 低信頼度の予測データ
    low_confidence_prediction = Prediction(
        prediction_date=today,
        target_date=today + timedelta(days=7),
        period=PredictionPeriod.ONE_WEEK,
        predicted_rate=Decimal("150.50"),
        prediction_strength=0.6,  # 70%未満
        model_version="test_v1.0"
    )
    db_session.add(low_confidence_prediction)
    await db_session.commit()
    
    # 予測信頼度アラートチェックを実行
    await service._check_prediction_confidence_alerts()
    
    # アラートが生成されたか確認
    result = await service.get_active_alerts()
    
    confidence_alerts = [
        alert for alert in result.alerts 
        if "信頼度" in alert.title
    ]
    
    assert len(confidence_alerts) >= 1
    confidence_alert = confidence_alerts[0]
    assert confidence_alert.severity == "medium"
    assert "60%" in confidence_alert.message


@pytest.mark.asyncio
async def test_data_quality_alert_generation(db_session: AsyncSession):
    """データ品質アラート生成テスト"""
    service = AlertsService(db_session)
    
    # 古いデータを作成（25時間前）
    old_time = datetime.now() - timedelta(hours=25)
    old_rate = ExchangeRate(
        date=date.today() - timedelta(days=1),
        close_rate=Decimal("150.00"),
        source=DataSourceType.YAHOO_FINANCE,
        created_at=old_time
    )
    db_session.add(old_rate)
    await db_session.commit()
    
    # データ品質アラートチェックを実行
    await service._check_data_quality_alerts()
    
    # アラートが生成されたか確認
    result = await service.get_active_alerts()
    
    data_quality_alerts = [
        alert for alert in result.alerts 
        if "更新遅延" in alert.title or "データ" in alert.title
    ]
    
    assert len(data_quality_alerts) >= 1
    data_alert = data_quality_alerts[0]
    assert data_alert.severity == "high"
    assert "時間遅延" in data_alert.message


@pytest.mark.asyncio
async def test_alert_priority_ordering(db_session: AsyncSession):
    """アラート優先度順序付けテスト"""
    service = AlertsService(db_session)
    
    # アラート設定を準備
    alert_setting = AlertSetting(
        name="優先度テスト設定",
        alert_type=AlertType.VOLATILITY_HIGH,
        is_enabled=True,
        conditions='{"test": true}',
        email_enabled=False,
        browser_notification_enabled=True
    )
    db_session.add(alert_setting)
    await db_session.commit()
    
    # 異なる重要度のアラートを作成
    critical_alert = await service._create_alert(
        title="緊急アラート",
        message="緊急事態です",
        severity="critical",
        alert_setting_id=alert_setting.id
    )
    
    medium_alert = await service._create_alert(
        title="中程度アラート",
        message="注意が必要です",
        severity="medium", 
        alert_setting_id=alert_setting.id
    )
    
    low_alert = await service._create_alert(
        title="軽微アラート",
        message="軽微な問題です",
        severity="low",
        alert_setting_id=alert_setting.id
    )
    
    # 中程度のアラートを確認済みにする
    medium_alert.is_acknowledged = True
    medium_alert.acknowledged_at = datetime.now()
    await db_session.commit()
    
    # 優先度順でアラートを取得
    result = await service.get_active_alerts()
    
    # 検証
    assert len(result.alerts) == 3
    assert result.unacknowledged_count == 2
    assert result.critical_count == 1
    
    # 最初のアラートは未確認のcriticalである
    first_alert = result.alerts[0]
    assert first_alert.severity == "critical"
    assert first_alert.is_acknowledged is False


@pytest.mark.asyncio
async def test_alert_summary_calculation(db_session: AsyncSession):
    """アラートサマリー計算テスト"""
    service = AlertsService(db_session)
    
    # アラート設定を準備
    alert_setting = AlertSetting(
        name="サマリーテスト設定",
        alert_type=AlertType.RATE_THRESHOLD,
        is_enabled=True,
        conditions='{"test": true}',
        email_enabled=False,
        browser_notification_enabled=True
    )
    db_session.add(alert_setting)
    await db_session.commit()
    
    # 様々な重要度のアラートを作成
    await service._create_alert("高重要度1", "メッセージ1", "high", alert_setting.id)
    await service._create_alert("高重要度2", "メッセージ2", "high", alert_setting.id) 
    await service._create_alert("中重要度1", "メッセージ3", "medium", alert_setting.id)
    await service._create_alert("緊急1", "メッセージ4", "critical", alert_setting.id)
    
    result = await service.get_active_alerts()
    
    # サマリー検証
    assert result.total_alerts == 4
    assert result.unacknowledged_count == 4
    assert result.critical_count == 1
    assert result.counts_by_severity["high"] == 2
    assert result.counts_by_severity["medium"] == 1
    assert result.counts_by_severity["critical"] == 1
    assert result.show_notification_badge is True
    assert result.requires_attention is True  # critical が1つ以上ある


@pytest.mark.asyncio
async def test_cleanup_old_alerts(db_session: AsyncSession):
    """古いアラートのクリーンアップテスト"""
    service = AlertsService(db_session)
    
    # アラート設定を準備
    alert_setting = AlertSetting(
        name="クリーンアップテスト設定",
        alert_type=AlertType.PREDICTION_CONFIDENCE_LOW,
        is_enabled=True,
        conditions='{"test": true}',
        email_enabled=False,
        browser_notification_enabled=True
    )
    db_session.add(alert_setting)
    await db_session.commit()
    
    # 古い確認済みアラートを作成（35日前）
    old_time = datetime.now() - timedelta(days=35)
    old_alert = ActiveAlert(
        alert_setting_id=alert_setting.id,
        title="古いアラート",
        message="35日前のアラート",
        severity="medium",
        is_acknowledged=True,
        acknowledged_at=old_time,
        created_at=old_time
    )
    db_session.add(old_alert)
    
    # 新しいアラートを作成
    new_alert = await service._create_alert(
        title="新しいアラート",
        message="最近のアラート",
        severity="medium",
        alert_setting_id=alert_setting.id
    )
    
    # クリーンアップ前のカウント
    result_before = await service.get_active_alerts()
    count_before = result_before.total_alerts
    
    # クリーンアップを実行
    await service._cleanup_old_alerts()
    
    # クリーンアップ後のカウント
    result_after = await service.get_active_alerts()
    count_after = result_after.total_alerts
    
    # 古いアラートが削除されたことを確認
    assert count_after < count_before
    
    # 新しいアラートは残っていることを確認
    remaining_titles = [alert.title for alert in result_after.alerts]
    assert "新しいアラート" in remaining_titles
    assert "古いアラート" not in remaining_titles


@pytest.mark.asyncio
async def test_duplicate_alert_prevention(db_session: AsyncSession):
    """重複アラート防止テスト"""
    service = AlertsService(db_session)
    
    today = date.today()
    
    # 既存のアラートを作成
    alert_setting = AlertSetting(
        name="重複防止テスト設定",
        alert_type=AlertType.RATE_THRESHOLD,
        is_enabled=True,
        conditions='{"test": true}',
        email_enabled=False,
        browser_notification_enabled=True
    )
    db_session.add(alert_setting)
    await db_session.commit()
    
    existing_alert = ActiveAlert(
        alert_setting_id=alert_setting.id,
        title="rate threshold アラート",
        message="既存のアラート",
        severity="medium",
        is_acknowledged=False,
        created_at=datetime.now()
    )
    db_session.add(existing_alert)
    await db_session.commit()
    
    # 既存アラートチェック
    duplicate_check = await service._check_existing_alert("rate_threshold", today)
    
    # 重複が検出されることを確認
    assert duplicate_check is not None
    assert duplicate_check.id == existing_alert.id