"""
Settings Service Phase S-3c Tests
=================================

設定操作サービスの単体テスト（Phase S-3c: 設定更新・テスト実行機能）
対象エンドポイント: 5.2, 5.4, 5.5
実データベース使用・依存性注入パターン
"""

import pytest
from decimal import Decimal
from datetime import datetime
from typing import List, Dict, Any
import json

from sqlalchemy.ext.asyncio import AsyncSession

from app.services.settings_service import SettingsService
from app.models import PredictionSetting, AlertSetting, AlertType
from app.schemas.settings import AlertCondition


class TestSettingsServicePhaseS3c:
    """Phase S-3c: 設定操作サービステストクラス"""
    
    # ===================================================================
    # 予測設定更新テスト (エンドポイント 5.2)
    # ===================================================================
    
    @pytest.mark.asyncio
    async def test_update_prediction_settings_basic(self, db_session) -> None:
        """基本的な予測設定更新テスト"""
        # 更新データ準備
        update_data = {
            "name": "updated_prediction_settings",
            "lstm_sequence_length": 75,
            "lstm_units": 64,
            "xgboost_n_estimators": 120,
            "xgboost_learning_rate": Decimal("0.08"),
            "confidence_threshold": Decimal("0.85"),
            "sensitivity_mode": "aggressive",
            "volatility_adjustment": False
        }
        
        # 更新実行
        result = await settings_service.update_prediction_settings(update_data)
        
        # 検証
        assert isinstance(result, PredictionSetting)
        assert result.name == "updated_prediction_settings"
        assert result.lstm_sequence_length == 75
        assert result.lstm_units == 64
        assert result.xgboost_n_estimators == 120
        assert result.xgboost_learning_rate == Decimal("0.08")
        assert result.confidence_threshold == Decimal("0.85")
        assert result.sensitivity_mode == "aggressive"
        assert result.volatility_adjustment is False
        assert result.updated_at is not None
    
    @pytest.mark.asyncio
    async def test_update_prediction_settings_model_weights(self, settings_service: SettingsService) -> None:
        """モデル重み更新テスト"""
        # 更新データ準備（モデル重み含む）
        new_weights = {
            "lstm_weight": 0.8,
            "xgboost_weight": 0.2,
            "ensemble_method": "dynamic_weighting",
            "description": "LSTM重視の構成"
        }
        
        update_data = {
            "prediction_model_weights": new_weights,
            "ensemble_method": "dynamic_weighting"
        }
        
        # 更新実行
        result = await settings_service.update_prediction_settings(update_data)
        
        # 検証
        assert isinstance(result, PredictionSetting)
        
        # JSONとして保存されたmodel_weightsを検証
        stored_weights = json.loads(result.model_weights)
        assert stored_weights["lstm_weight"] == 0.8
        assert stored_weights["xgboost_weight"] == 0.2
        assert stored_weights["ensemble_method"] == "dynamic_weighting"
        assert stored_weights["description"] == "LSTM重視の構成"
    
    @pytest.mark.asyncio
    async def test_update_prediction_settings_partial_update(self, settings_service: SettingsService) -> None:
        """部分更新テスト（一部フィールドのみ更新）"""
        # 部分更新データ
        update_data = {
            "lstm_sequence_length": 90,
            "confidence_threshold": Decimal("0.75")
        }
        
        # 更新実行
        result = await settings_service.update_prediction_settings(update_data)
        
        # 検証: 指定されたフィールドのみ更新されること
        assert isinstance(result, PredictionSetting)
        assert result.lstm_sequence_length == 90
        assert result.confidence_threshold == Decimal("0.75")
        
        # 他のフィールドはデフォルト値またはそのまま残存
        assert result.updated_at is not None
    
    @pytest.mark.asyncio
    async def test_update_prediction_settings_creates_default_if_none_exists(self, db_session: AsyncSession) -> None:
        """設定が存在しない場合のデフォルト作成+更新テスト"""
        # 全設定を無効化してクリーンな状態を作る
        from sqlalchemy import update
        await db_session.execute(
            update(PredictionSetting).values(is_active=False).where(PredictionSetting.is_active == True)
        )
        await db_session.commit()
        
        service = SettingsService(db_session)
        
        # 更新データ
        update_data = {
            "name": "first_setting",
            "sensitivity_mode": "conservative"
        }
        
        # 更新実行（デフォルト作成から開始）
        result = await service.update_prediction_settings(update_data)
        
        # 検証: デフォルト設定がベースとして作成され、更新データが反映される
        assert isinstance(result, PredictionSetting)
        assert result.name == "first_setting"
        assert result.sensitivity_mode == "conservative"
        assert result.is_active is True
    
    # ===================================================================
    # アラート設定更新テスト (エンドポイント 5.4)
    # ===================================================================
    
    @pytest.mark.asyncio
    async def test_update_alert_settings_basic(self, db_session: AsyncSession) -> None:
        """基本的なアラート設定更新テスト"""
        # 事前データ準備（更新対象のアラート設定を作成）
        initial_alert = AlertSetting(
            name="更新前アラート",
            alert_type=AlertType.RATE_THRESHOLD,
            is_enabled=False,
            conditions=json.dumps({"threshold_rate": "145.0", "comparison_operator": "gte"}),
            email_enabled=False,
            browser_notification_enabled=True,
            cooldown_minutes=60,
            max_alerts_per_day=5
        )
        
        db_session.add(initial_alert)
        await db_session.commit()
        await db_session.refresh(initial_alert)
        
        # サービス準備
        service = SettingsService(db_session)
        
        # 更新データ
        update_data = {
            "name": "更新後アラート",
            "is_enabled": True,
            "email_enabled": True,
            "email_address": "updated@example.com",
            "cooldown_minutes": 30,
            "max_alerts_per_day": 10
        }
        
        # 更新実行
        result = await service.update_alert_settings(initial_alert.id, update_data)
        
        # 検証
        assert isinstance(result, AlertSetting)
        assert result.id == initial_alert.id
        assert result.name == "更新後アラート"
        assert result.is_enabled is True
        assert result.email_enabled is True
        assert result.email_address == "updated@example.com"
        assert result.cooldown_minutes == 30
        assert result.max_alerts_per_day == 10
        assert result.updated_at is not None
    
    @pytest.mark.asyncio
    async def test_update_alert_settings_with_conditions(self, db_session: AsyncSession) -> None:
        """アラート条件更新テスト"""
        # 事前データ準備
        initial_alert = AlertSetting(
            name="条件更新テスト",
            alert_type=AlertType.VOLATILITY_HIGH,
            is_enabled=True,
            conditions=json.dumps({"volatility_threshold": "2.0"}),
            email_enabled=False,
            browser_notification_enabled=True,
            cooldown_minutes=120,
            max_alerts_per_day=3
        )
        
        db_session.add(initial_alert)
        await db_session.commit()
        await db_session.refresh(initial_alert)
        
        # サービス準備
        service = SettingsService(db_session)
        
        # 新しいアラート条件
        new_conditions = AlertCondition(
            volatility_threshold=Decimal("3.5"),
            confidence_threshold=Decimal("0.8")
        )
        
        update_data = {
            "conditions": new_conditions,
            "cooldown_minutes": 90
        }
        
        # 更新実行
        result = await service.update_alert_settings(initial_alert.id, update_data)
        
        # 検証
        assert isinstance(result, AlertSetting)
        assert result.cooldown_minutes == 90
        
        # JSONとして保存された条件を確認
        stored_conditions = json.loads(result.conditions)
        assert stored_conditions["volatility_threshold"] == "3.5"
        assert stored_conditions["confidence_threshold"] == "0.8"
    
    @pytest.mark.asyncio
    async def test_update_alert_settings_nonexistent_id(self, settings_service: SettingsService) -> None:
        """存在しないIDでの更新エラーテスト"""
        nonexistent_id = 99999
        update_data = {"name": "存在しないアラート"}
        
        # 更新実行（エラーが発生することを確認）
        with pytest.raises(ValueError) as exc_info:
            await settings_service.update_alert_settings(nonexistent_id, update_data)
        
        assert f"Alert setting with ID {nonexistent_id} not found" in str(exc_info.value)
    
    # ===================================================================
    # 予測設定テスト実行機能テスト (エンドポイント 5.5)
    # ===================================================================
    
    @pytest.mark.asyncio
    async def test_test_prediction_settings_success(self) -> None:
        """予測設定テスト実行成功ケース"""
        # 実データベースに直接接続
        from app.database import AsyncSessionLocal
        async with AsyncSessionLocal() as db_session:
            # サービス作成とテスト実行
            settings_service = SettingsService(db_session)
            result = await settings_service.test_prediction_settings()
            
            # 検証
            assert isinstance(result, dict)
            assert result["success"] is True
            assert result["test_prediction"] is not None
            assert isinstance(result["test_prediction"], Decimal)
            assert result["test_prediction"] > 0
            
            # 信頼区間の検証
            assert result["confidence_interval"] is not None
            confidence_lower, confidence_upper = result["confidence_interval"]
            assert isinstance(confidence_lower, Decimal)
            assert isinstance(confidence_upper, Decimal)
            assert confidence_lower < confidence_upper
            
            # パフォーマンス指標の検証
            performance = result["prediction_model_performance"]
            assert isinstance(performance, dict)
            assert "lstm_accuracy" in performance
            assert "xgboost_accuracy" in performance
            assert "ensemble_accuracy" in performance
            assert "mae" in performance
            assert "rmse" in performance
            assert "sharpe_ratio" in performance
            assert "feature_importance" in performance
            
            # 実行時間の検証
            assert result["execution_time_ms"] > 0
            assert isinstance(result["execution_time_ms"], int)
            
            # メッセージとタイムスタンプの検証
            assert result["message"] is not None
            assert isinstance(result["message"], str)
            assert result["tested_at"] is not None
            assert isinstance(result["tested_at"], datetime)
            
            # テストパラメータの検証
            test_params = result["test_parameters"]
            assert isinstance(test_params, dict)
            assert "lstm_enabled" in test_params
            assert "xgboost_enabled" in test_params
            assert "ensemble_method" in test_params
            assert "sensitivity_mode" in test_params
    
    @pytest.mark.asyncio
    async def test_test_prediction_settings_with_custom_parameters(self, db_session: AsyncSession) -> None:
        """カスタム設定での予測テスト実行"""
        # カスタム予測設定を作成
        from sqlalchemy import update
        await db_session.execute(
            update(PredictionSetting).values(is_active=False).where(PredictionSetting.is_active == True)
        )
        
        custom_setting = PredictionSetting(
            name="custom_test_settings",
            is_active=True,
            model_weights='{"lstm_weight": 0.9, "xgboost_weight": 0.1}',
            lstm_enabled=True,
            lstm_sequence_length=30,  # 短いシーケンス（警告が出るはず）
            lstm_layers=1,
            lstm_units=25,  # 少ないユニット（警告が出るはず）
            xgboost_enabled=True,
            xgboost_n_estimators=40,  # 少ない推定器（警告が出るはず）
            xgboost_max_depth=4,
            xgboost_learning_rate=Decimal("0.35"),  # 高い学習率（警告が出るはず）
            ensemble_method="weighted_average",
            confidence_threshold=Decimal("0.95"),  # 高い閾値（情報メッセージが出るはず）
            sensitivity_mode="aggressive",
            volatility_adjustment=True
        )
        
        db_session.add(custom_setting)
        await db_session.commit()
        
        service = SettingsService(db_session)
        
        # テスト実行
        result = await service.test_prediction_settings()
        
        # 検証
        assert isinstance(result, dict)
        assert result["success"] is True
        
        # 警告メッセージが含まれることを確認
        message = result["message"]
        assert "Warning" in message or "Info" in message
    
    @pytest.mark.asyncio
    async def test_test_prediction_settings_performance_metrics_validation(self, settings_service: SettingsService) -> None:
        """パフォーマンス指標の詳細検証"""
        # テスト実行
        result = await settings_service.test_prediction_settings()
        
        # パフォーマンス指標の詳細検証
        performance = result["prediction_model_performance"]
        
        # 精度指標の範囲確認
        assert 0.0 <= performance["lstm_accuracy"] <= 1.0
        assert 0.0 <= performance["xgboost_accuracy"] <= 1.0
        assert 0.0 <= performance["ensemble_accuracy"] <= 1.0
        
        # エラー指標の正数確認
        assert performance["mae"] > 0
        assert performance["rmse"] > 0
        
        # シャープレシオの妥当性
        assert performance["sharpe_ratio"] > 0
        
        # 特徴量重要度の確認
        feature_importance = performance["feature_importance"]
        assert isinstance(feature_importance, dict)
        
        # 重要度の合計が1.0に近いことを確認
        total_importance = sum(feature_importance.values())
        assert 0.9 <= total_importance <= 1.1
        
        # 主要な特徴量が含まれることを確認
        expected_features = ["sma_5", "sma_25", "rsi_14", "macd", "volatility", "previous_rate"]
        for feature in expected_features:
            assert feature in feature_importance
            assert 0.0 <= feature_importance[feature] <= 1.0

    # ===================================================================
    # エラーハンドリングテスト
    # ===================================================================
    
    @pytest.mark.asyncio
    async def test_update_prediction_settings_database_error(self, db_session: AsyncSession) -> None:
        """予測設定更新時のデータベースエラー処理"""
        service = SettingsService(db_session)
        
        # データベース接続を閉じてエラー状況を作る
        await db_session.close()
        
        update_data = {"name": "error_test"}
        
        # エラーが適切に伝播されることを確認
        with pytest.raises(Exception):
            await service.update_prediction_settings(update_data)
    
    @pytest.mark.asyncio 
    async def test_test_prediction_settings_with_no_active_settings(self, db_session: AsyncSession) -> None:
        """アクティブな設定がない場合のテスト実行"""
        # 全設定を無効化
        from sqlalchemy import update
        await db_session.execute(
            update(PredictionSetting).values(is_active=False).where(PredictionSetting.is_active == True)
        )
        await db_session.commit()
        
        service = SettingsService(db_session)
        
        # テスト実行（デフォルト設定が作成されて実行される）
        result = await service.test_prediction_settings()
        
        # 検証: デフォルト設定でテストが実行される
        assert isinstance(result, dict)
        assert result["success"] is True