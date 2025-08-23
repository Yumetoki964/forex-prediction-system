"""
Settings Service Tests
=====================

設定サービスの単体テスト（実データベース使用）
Phase S-1b担当: エンドポイント 5.1, 5.3
"""

import pytest
from decimal import Decimal
from datetime import datetime
from typing import List, Optional

from sqlalchemy.ext.asyncio import AsyncSession

from app.services.settings_service import SettingsService
from app.models import PredictionSetting, AlertSetting, AlertType
from app.schemas.settings import PredictionSettingsResponse, AlertSettingsResponse, AlertCondition


class TestSettingsService:
    """設定サービステストクラス（実データベース使用）"""
    
    @pytest.fixture
    def settings_service(self, db_session: AsyncSession) -> SettingsService:
        """設定サービスのフィクスチャ"""
        return SettingsService(db_session)
    
    # ===================================================================
    # 予測設定取得テスト (エンドポイント 5.1)
    # ===================================================================
    
    @pytest.mark.asyncio
    async def test_get_prediction_settings_with_existing_data(self, settings_service: SettingsService) -> None:
        """既存データがある場合の予測設定取得テスト（実データベース使用）"""
        # 実データベースに直接接続
        from app.database import AsyncSessionLocal
        async with AsyncSessionLocal() as db_session:
            # 実データベースに事前データを作成
            test_setting = PredictionSetting(
                name="test_settings_existing",
                is_active=True,
                model_weights='{"lstm_weight": 0.7, "xgboost_weight": 0.3}',
                lstm_enabled=True,
                lstm_sequence_length=45,
                lstm_layers=3,
                lstm_units=64,
                xgboost_enabled=True,
                xgboost_n_estimators=150,
                xgboost_max_depth=8,
                xgboost_learning_rate=Decimal("0.05"),
                ensemble_method="weighted_average",
                confidence_threshold=Decimal("0.8"),
                sensitivity_mode="conservative",
                volatility_adjustment=False
            )
            
            # 既存のアクティブ設定を無効にする
            from sqlalchemy import update
            await db_session.execute(
                update(PredictionSetting).values(is_active=False).where(PredictionSetting.is_active == True)
            )
            
            # テストデータを挿入
            db_session.add(test_setting)
            await db_session.commit()
            await db_session.refresh(test_setting)
            
            # テスト実行
            test_service = SettingsService(db_session)
            result: PredictionSettingsResponse = await test_service.get_prediction_settings()
            
            # 検証
            assert isinstance(result, PredictionSettingsResponse)
            assert result.id == test_setting.id
            assert result.name == "test_settings_existing"
            assert result.is_active is True
            assert result.prediction_model_weights["lstm_weight"] == 0.7
            assert result.prediction_model_weights["xgboost_weight"] == 0.3
            assert result.lstm_sequence_length == 45
            assert result.lstm_layers == 3
            assert result.lstm_units == 64
            assert result.xgboost_n_estimators == 150
            assert result.xgboost_max_depth == 8
            assert result.xgboost_learning_rate == Decimal("0.05")
            assert result.ensemble_method == "weighted_average"
            assert result.confidence_threshold == Decimal("0.8")
            assert result.sensitivity_mode == "conservative"
            assert result.volatility_adjustment is False
    
    @pytest.mark.asyncio
    async def test_get_prediction_settings_creates_default_when_none_exists(self, settings_service: SettingsService, db_session: AsyncSession) -> None:
        """データが存在しない場合のデフォルト設定作成テスト（実データベース使用）"""
        # 既存の全ての予測設定を無効にして、データが存在しない状況を作る
        from sqlalchemy import update
        await db_session.execute(
            update(PredictionSetting).values(is_active=False).where(PredictionSetting.is_active == True)
        )
        await db_session.commit()
        
        # テスト実行
        result: PredictionSettingsResponse = await settings_service.get_prediction_settings()
        
        # 検証: デフォルト設定が作成されることを確認
        assert isinstance(result, PredictionSettingsResponse)
        assert result.name == "default_prediction_settings"
        assert result.is_active is True
        assert result.prediction_model_weights["lstm_weight"] == 0.6
        assert result.prediction_model_weights["xgboost_weight"] == 0.4
        assert result.lstm_enabled is True
        assert result.lstm_sequence_length == 60
        assert result.lstm_layers == 2
        assert result.lstm_units == 50
        assert result.xgboost_enabled is True
        assert result.xgboost_n_estimators == 100
        assert result.xgboost_max_depth == 6
        assert result.xgboost_learning_rate == Decimal("0.1")
        assert result.ensemble_method == "weighted_average"
        assert result.confidence_threshold == Decimal("0.7")
        assert result.sensitivity_mode == "standard"
        assert result.volatility_adjustment is True
    
    @pytest.mark.asyncio
    async def test_get_prediction_settings_handles_invalid_json(self, settings_service: SettingsService, mock_db_session: AsyncSession) -> None:
        """不正なJSONを含む設定の処理テスト"""
        # 不正なJSONを持つ設定を作成
        test_setting = PredictionSetting(
            id=1,
            name="invalid_json_settings",
            is_active=True,
            model_weights='{"invalid_json": }',  # 不正なJSON
            lstm_enabled=True,
            lstm_sequence_length=60,
            lstm_layers=2,
            lstm_units=50,
            xgboost_enabled=True,
            xgboost_n_estimators=100,
            xgboost_max_depth=6,
            xgboost_learning_rate=Decimal("0.1"),
            ensemble_method="weighted_average",
            confidence_threshold=Decimal("0.7"),
            sensitivity_mode="standard",
            volatility_adjustment=True,
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
        
        # モックの設定
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = test_setting
        mock_db_session.execute.return_value = mock_result
        
        # テスト実行
        result: PredictionSettingsResponse = await settings_service.get_prediction_settings()
        
        # 検証: 不正なJSONの場合はデフォルト値が使用される
        assert isinstance(result, PredictionSettingsResponse)
        assert result.prediction_model_weights["lstm_weight"] == 0.6
        assert result.prediction_model_weights["xgboost_weight"] == 0.4
    
    # ===================================================================
    # アラート設定取得テスト (エンドポイント 5.3)
    # ===================================================================
    
    @pytest.mark.asyncio
    async def test_get_alert_settings_with_existing_data(self, settings_service: SettingsService, mock_db_session: AsyncSession) -> None:
        """既存データがある場合のアラート設定取得テスト"""
        # 事前データ準備
        test_alert1 = AlertSetting(
            id=1,
            name="テストアラート1",
            alert_type=AlertType.RATE_THRESHOLD,
            is_enabled=True,
            conditions='{"threshold_rate": "145.0", "comparison_operator": "gte"}',
            email_enabled=False,
            browser_notification_enabled=True,
            cooldown_minutes=30,
            max_alerts_per_day=8,
            triggered_count=2,
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
        
        test_alert2 = AlertSetting(
            id=2,
            name="テストアラート2",
            alert_type=AlertType.SIGNAL_CHANGE,
            is_enabled=False,
            conditions='{"signal_types": ["strong_sell"], "confidence_threshold": "0.85"}',
            email_enabled=True,
            browser_notification_enabled=False,
            email_address="test@example.com",
            cooldown_minutes=60,
            max_alerts_per_day=5,
            triggered_count=0,
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
        
        # モックの設定
        mock_result = MagicMock()
        mock_result.scalars.return_value.all.return_value = [test_alert1, test_alert2]
        mock_db_session.execute.return_value = mock_result
        
        # テスト実行
        result: List[AlertSettingsResponse] = await settings_service.get_alert_settings()
        
        # 検証
        assert isinstance(result, list)
        assert len(result) == 2
        
        # 1つ目のアラート設定確認
        alert1 = next((a for a in result if a.name == "テストアラート1"), None)
        assert alert1 is not None
        assert alert1.alert_type == "rate_threshold"
        assert alert1.is_enabled is True
        assert alert1.conditions.threshold_rate == Decimal("145.0")
        assert alert1.conditions.comparison_operator == "gte"
        assert alert1.email_enabled is False
        assert alert1.browser_notification_enabled is True
        assert alert1.cooldown_minutes == 30
        assert alert1.max_alerts_per_day == 8
        assert alert1.triggered_count == 2
        
        # 2つ目のアラート設定確認
        alert2 = next((a for a in result if a.name == "テストアラート2"), None)
        assert alert2 is not None
        assert alert2.alert_type == "signal_change"
        assert alert2.is_enabled is False
        assert alert2.conditions.signal_types == ["strong_sell"]
        assert alert2.conditions.confidence_threshold == Decimal("0.85")
        assert alert2.email_enabled is True
        assert alert2.browser_notification_enabled is False
        assert alert2.email_address == "test@example.com"
    
    @pytest.mark.asyncio
    async def test_get_alert_settings_with_filters(self, settings_service: SettingsService, mock_db_session: AsyncSession) -> None:
        """フィルタリング機能のテスト"""
        # 事前データ準備（複数タイプのアラート）
        alerts = [
            AlertSetting(
                id=1,
                name="有効レートアラート",
                alert_type=AlertType.RATE_THRESHOLD,
                is_enabled=True,
                conditions='{"threshold_rate": "150.0"}',
                email_enabled=False,
                browser_notification_enabled=True,
                cooldown_minutes=60,
                max_alerts_per_day=5,
                created_at=datetime.now(),
                updated_at=datetime.now()
            ),
            AlertSetting(
                id=2,
                name="無効レートアラート",
                alert_type=AlertType.RATE_THRESHOLD,
                is_enabled=False,
                conditions='{"threshold_rate": "140.0"}',
                email_enabled=False,
                browser_notification_enabled=True,
                cooldown_minutes=60,
                max_alerts_per_day=5,
                created_at=datetime.now(),
                updated_at=datetime.now()
            ),
            AlertSetting(
                id=3,
                name="有効シグナルアラート",
                alert_type=AlertType.SIGNAL_CHANGE,
                is_enabled=True,
                conditions='{"signal_types": ["buy"]}',
                email_enabled=True,
                browser_notification_enabled=True,
                cooldown_minutes=30,
                max_alerts_per_day=10,
                created_at=datetime.now(),
                updated_at=datetime.now()
            )
        ]
        
        # フィルタリング用のモック設定
        def mock_execute(stmt):
            mock_result = MagicMock()
            # クエリの内容に基づいてフィルタリング結果を返す
            mock_result.scalars.return_value.all.return_value = alerts[:2]  # レートアラートのみ
            return mock_result
        
        mock_db_session.execute = mock_execute
        
        # テスト1: アラートタイプでフィルタリング
        rate_alerts = await settings_service.get_alert_settings(alert_type="rate_threshold")
        assert len(rate_alerts) == 2
        assert all(alert.alert_type == "rate_threshold" for alert in rate_alerts)
    
    @pytest.mark.asyncio
    async def test_get_alert_settings_creates_default_when_none_exists(self, settings_service: SettingsService, mock_db_session: AsyncSession) -> None:
        """データが存在しない場合のデフォルト設定作成テスト"""
        # モックの設定: データが存在しない場合
        mock_result = MagicMock()
        mock_result.scalars.return_value.all.return_value = []
        mock_db_session.execute.return_value = mock_result
        
        # デフォルト作成時のモック設定
        mock_db_session.add.return_value = None
        mock_db_session.commit.return_value = None
        mock_db_session.refresh.return_value = None
        
        # テスト実行
        result: List[AlertSettingsResponse] = await settings_service.get_alert_settings()
        
        # 検証: 4つのデフォルトアラートが作成される
        assert isinstance(result, list)
        assert len(result) == 4
        
        alert_types = [alert.alert_type for alert in result]
        assert "rate_threshold" in alert_types
        assert "signal_change" in alert_types
        assert "volatility_high" in alert_types
        assert "prediction_confidence_low" in alert_types
        
        # 各アラートの基本プロパティを確認
        for alert in result:
            assert isinstance(alert.id, int)
            assert isinstance(alert.name, str)
            assert alert.name != ""
            assert isinstance(alert.conditions, AlertCondition)
            assert isinstance(alert.cooldown_minutes, int)
            assert alert.cooldown_minutes >= 0
            assert isinstance(alert.max_alerts_per_day, int)
            assert alert.max_alerts_per_day > 0
    
    # ===================================================================
    # ヘルパーメソッドテスト
    # ===================================================================
    
    @pytest.mark.asyncio
    async def test_get_prediction_setting_by_id(self, settings_service: SettingsService, mock_db_session: AsyncSession) -> None:
        """ID指定での予測設定取得テスト"""
        # 事前データ準備
        test_setting = PredictionSetting(
            id=1,
            name="ID指定テスト",
            is_active=True,
            model_weights='{"test": true}',
            lstm_enabled=True,
            lstm_sequence_length=60,
            lstm_layers=2,
            lstm_units=50,
            xgboost_enabled=True,
            xgboost_n_estimators=100,
            xgboost_max_depth=6,
            xgboost_learning_rate=Decimal("0.1"),
            ensemble_method="weighted_average",
            confidence_threshold=Decimal("0.7"),
            sensitivity_mode="standard",
            volatility_adjustment=True,
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
        
        # モックの設定
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = test_setting
        mock_db_session.execute.return_value = mock_result
        
        # テスト実行
        result = await settings_service.get_prediction_setting_by_id(1)
        
        # 検証
        assert result is not None
        assert result.id == 1
        assert result.name == "ID指定テスト"
    
    @pytest.mark.asyncio
    async def test_get_alert_setting_by_id(self, settings_service: SettingsService, mock_db_session: AsyncSession) -> None:
        """ID指定でのアラート設定取得テスト"""
        # 事前データ準備
        test_alert = AlertSetting(
            id=1,
            name="ID指定アラート",
            alert_type=AlertType.RATE_THRESHOLD,
            is_enabled=True,
            conditions='{"test": true}',
            email_enabled=False,
            browser_notification_enabled=True,
            cooldown_minutes=60,
            max_alerts_per_day=5,
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
        
        # モックの設定
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = test_alert
        mock_db_session.execute.return_value = mock_result
        
        # テスト実行
        result = await settings_service.get_alert_setting_by_id(1)
        
        # 検証
        assert result is not None
        assert result.id == 1
        assert result.name == "ID指定アラート"
    
    @pytest.mark.asyncio
    async def test_check_database_connection(self, settings_service: SettingsService, mock_db_session: AsyncSession) -> None:
        """データベース接続確認テスト"""
        # モックの設定（正常な場合）
        mock_result = MagicMock()
        mock_db_session.execute.return_value = mock_result
        
        # テスト実行
        result = await settings_service.check_database_connection()
        
        # 検証: データベース接続が成功する
        assert result is True


class TestSettingsServiceErrorHandling:
    """設定サービスのエラーハンドリングテスト"""
    
    @pytest.fixture
    def mock_db_session(self) -> AsyncSession:
        """モックデータベースセッション"""
        session = AsyncMock(spec=AsyncSession)
        return session
    
    @pytest.fixture
    def settings_service(self, mock_db_session) -> SettingsService:
        """設定サービスのフィクスチャ"""
        return SettingsService(mock_db_session)
    
    @pytest.mark.asyncio
    async def test_get_prediction_settings_database_error_handling(self, settings_service: SettingsService, mock_db_session: AsyncSession) -> None:
        """予測設定取得時のデータベースエラーハンドリングテスト"""
        # モックの設定（エラー発生）
        mock_db_session.execute.side_effect = Exception("Database connection failed")
        
        # テスト実行: エラーが発生することを確認
        with pytest.raises(Exception):
            await settings_service.get_prediction_settings()
    
    @pytest.mark.asyncio
    async def test_get_alert_settings_database_error_handling(self, settings_service: SettingsService, mock_db_session: AsyncSession) -> None:
        """アラート設定取得時のデータベースエラーハンドリングテスト"""
        # モックの設定（エラー発生）
        mock_db_session.execute.side_effect = Exception("Database connection failed")
        
        # テスト実行: エラーが発生することを確認
        with pytest.raises(Exception):
            await settings_service.get_alert_settings()