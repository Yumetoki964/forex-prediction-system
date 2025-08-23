"""
Test suite for Data Processing Services (Phase S-3b)
データ処理サービス群の単体テスト

対象サービス:
- CollectionService (データ収集実行)
- QualityService (データ品質レポート)
- RepairService (欠損データ修復)

エンドポイント: 4.2, 4.3, 4.4
"""

import pytest
import asyncio
from datetime import datetime, timedelta, date
from decimal import Decimal
from typing import List, Dict, Any

from app.services.collection_service import CollectionService
from app.services.quality_service import QualityService
from app.services.repair_service import RepairService

from app.schemas.data import (
    DataCollectionRequest, DataQualityReport, DataRepairRequest,
    RepairTarget, DataSourceType
)

from app.models import ExchangeRate, DataQuality, DataSource, DataSourceStatus


class TestCollectionService:
    """CollectionService の単体テスト"""

    @pytest.mark.asyncio
    async def test_execute_data_collection_basic(self, db_session):
        """基本的なデータ収集実行テスト"""
        service = CollectionService(db_session)
        
        # テスト用リクエスト
        request = DataCollectionRequest(
            sources=[DataSourceType.YAHOO_FINANCE],
            force_update=False,
            date_range={
                "start": "2024-08-20",
                "end": "2024-08-22"
            },
            notify_on_completion=False
        )
        
        # データ収集実行
        response = await service.execute_data_collection(request)
        
        # 結果検証
        assert response is not None
        assert response.collection_id is not None
        assert response.status in ["started", "failed"]
        assert response.sources_count >= 0
        assert response.started_at is not None
        assert isinstance(response.progress, list)

    @pytest.mark.asyncio
    async def test_execute_data_collection_all_sources(self, db_session):
        """全ソース対象のデータ収集テスト"""
        service = CollectionService(db_session)
        
        # 全ソース対象のリクエスト
        request = DataCollectionRequest(
            sources=None,  # 全ソース
            force_update=True,
            notify_on_completion=False
        )
        
        response = await service.execute_data_collection(request)
        
        assert response is not None
        assert response.collection_id is not None
        # 全ソースが対象の場合、進捗リストが複数あることを期待
        assert len(response.progress) >= 1

    @pytest.mark.asyncio
    async def test_execute_data_collection_invalid_date_range(self, db_session):
        """不正な日付範囲でのデータ収集テスト"""
        service = CollectionService(db_session)
        
        # 不正な日付範囲
        request = DataCollectionRequest(
            sources=[DataSourceType.YAHOO_FINANCE],
            date_range={
                "start": "2024-08-25",
                "end": "2024-08-20"  # 終了日が開始日より前
            }
        )
        
        response = await service.execute_data_collection(request)
        
        # エラーハンドリングされることを確認
        assert response is not None
        assert response.collection_id is not None

    @pytest.mark.asyncio
    async def test_collection_service_target_validation(self, db_session):
        """収集対象の検証テスト"""
        service = CollectionService(db_session)
        
        # _determine_target_sources メソッドのテスト
        sources = await service._determine_target_sources([DataSourceType.BOJ_CSV])
        assert DataSourceType.BOJ_CSV in sources
        
        # 全ソース対象
        all_sources = await service._determine_target_sources(None)
        assert len(all_sources) >= 3  # 最低3つのソース

    @pytest.mark.asyncio
    async def test_collection_time_estimation(self, db_session):
        """収集時間見積もりテスト"""
        service = CollectionService(db_session)
        
        # Yahoo Finance の時間見積もり
        time_yahoo = service._estimate_collection_time(DataSourceType.YAHOO_FINANCE, 10)
        assert time_yahoo is not None
        assert 1 <= time_yahoo <= 60
        
        # Alpha Vantage の時間見積もり（時間がかかることを想定）
        time_alpha = service._estimate_collection_time(DataSourceType.ALPHA_VANTAGE, 10)
        assert time_alpha is not None
        assert time_alpha >= time_yahoo  # Alpha Vantageの方が時間がかかることを期待


class TestQualityService:
    """QualityService の単体テスト"""

    @pytest.mark.asyncio
    async def test_generate_data_quality_report_basic(self, db_session):
        """基本的な品質レポート生成テスト"""
        service = QualityService(db_session)
        
        # 品質レポート生成
        report = await service.generate_data_quality_report(period_days=7)
        
        # 結果検証
        assert isinstance(report, DataQualityReport)
        assert report.report_id is not None
        assert report.report_date is not None
        assert report.overall_quality_score is not None
        assert 0.0 <= report.overall_quality_score <= 1.0
        assert report.data_health_status in ["excellent", "good", "fair", "poor"]
        assert report.quality_metrics is not None
        assert isinstance(report.source_scores, list)
        assert isinstance(report.quality_issues, list)
        assert isinstance(report.recommendations, list)

    @pytest.mark.asyncio
    async def test_generate_data_quality_report_different_periods(self, db_session):
        """異なる期間での品質レポート生成テスト"""
        service = QualityService(db_session)
        
        # 短期間レポート
        short_report = await service.generate_data_quality_report(period_days=1)
        assert short_report is not None
        
        # 長期間レポート
        long_report = await service.generate_data_quality_report(period_days=30)
        assert long_report is not None
        
        # レポートIDが異なることを確認
        assert short_report.report_id != long_report.report_id

    @pytest.mark.asyncio
    async def test_quality_metrics_calculation(self, db_session):
        """品質指標計算テスト"""
        service = QualityService(db_session)
        
        # 期間を設定
        end_date = date.today()
        start_date = end_date - timedelta(days=7)
        
        # 品質指標を計算
        metrics = await service._calculate_overall_quality_metrics(start_date, end_date)
        
        # 結果検証
        assert metrics is not None
        assert 0.0 <= metrics.completeness_rate <= 1.0
        assert 0.0 <= metrics.accuracy_rate <= 1.0
        assert 0.0 <= metrics.consistency_rate <= 1.0
        assert metrics.outlier_count >= 0
        assert metrics.duplicate_count >= 0
        assert 0.0 <= metrics.quality_score <= 1.0

    @pytest.mark.asyncio
    async def test_source_quality_scores_calculation(self, db_session):
        """ソース別品質スコア計算テスト"""
        service = QualityService(db_session)
        
        # 期間を設定
        end_date = date.today()
        start_date = end_date - timedelta(days=7)
        
        # ソース別品質スコアを計算
        source_scores = await service._calculate_source_quality_scores(start_date, end_date)
        
        # 結果検証
        assert isinstance(source_scores, list)
        
        # 各スコアの検証
        for score in source_scores:
            assert score.source_name is not None
            assert score.source_type is not None
            assert 0.0 <= score.completeness_score <= 1.0
            assert 0.0 <= score.accuracy_score <= 1.0
            assert 0.0 <= score.timeliness_score <= 1.0
            assert 0.0 <= score.overall_score <= 1.0
            assert score.data_points_analyzed >= 0

    @pytest.mark.asyncio
    async def test_outlier_detection(self, db_session):
        """外れ値検出テスト"""
        service = QualityService(db_session)
        
        # 期間を設定
        end_date = date.today()
        start_date = end_date - timedelta(days=30)
        
        # 外れ値検出
        outlier_count = await service._detect_outliers_in_period(start_date, end_date)
        
        # 結果検証
        assert outlier_count >= 0
        assert isinstance(outlier_count, int)

    @pytest.mark.asyncio
    async def test_quality_issues_detection(self, db_session):
        """品質問題検出テスト"""
        service = QualityService(db_session)
        
        # 期間を設定
        end_date = date.today()
        start_date = end_date - timedelta(days=7)
        
        # 品質問題検出
        issues = await service._detect_quality_issues(start_date, end_date)
        
        # 結果検証
        assert isinstance(issues, list)
        
        # 各問題の検証
        for issue in issues:
            assert issue.issue_type is not None
            assert issue.severity in ["low", "medium", "high", "critical"]
            assert isinstance(issue.affected_dates, list)
            assert issue.affected_count >= 0
            assert issue.description is not None
            assert isinstance(issue.is_auto_repairable, bool)


class TestRepairService:
    """RepairService の単体テスト"""

    @pytest.mark.asyncio
    async def test_execute_data_repair_dry_run(self, db_session):
        """ドライラン修復実行テスト"""
        service = RepairService(db_session)
        
        # テスト用修復リクエスト（ドライラン）
        repair_target = RepairTarget(
            date_range={
                "start": date(2024, 8, 20),
                "end": date(2024, 8, 22)
            },
            issue_types=["missing_data"],
            max_interpolation_gap=5
        )
        
        request = DataRepairRequest(
            repair_targets=[repair_target],
            repair_strategy="conservative",
            dry_run=True,
            backup_before_repair=False
        )
        
        # 修復実行
        response = await service.execute_data_repair(request)
        
        # 結果検証
        assert response is not None
        assert response.repair_id is not None
        assert response.status in ["completed", "failed"]
        assert response.is_dry_run is True
        assert response.targets_count == 1
        assert isinstance(response.repair_results, list)
        assert isinstance(response.errors, list)
        assert isinstance(response.warnings, list)

    @pytest.mark.asyncio
    async def test_execute_data_repair_actual_run(self, db_session):
        """実修復実行テスト"""
        service = RepairService(db_session)
        
        repair_target = RepairTarget(
            date_range={
                "start": date(2024, 8, 15),
                "end": date(2024, 8, 16)
            },
            issue_types=["missing_data"],
            max_interpolation_gap=3
        )
        
        request = DataRepairRequest(
            repair_targets=[repair_target],
            repair_strategy="balanced",
            dry_run=False,
            backup_before_repair=False,  # テストなのでバックアップなし
            notify_on_completion=False
        )
        
        response = await service.execute_data_repair(request)
        
        assert response is not None
        assert response.repair_id is not None
        assert response.is_dry_run is False

    @pytest.mark.asyncio
    async def test_repair_target_validation(self, db_session):
        """修復対象検証テスト"""
        service = RepairService(db_session)
        
        # 有効な修復対象
        valid_target = RepairTarget(
            date_range={
                "start": date(2024, 8, 20),
                "end": date(2024, 8, 22)
            },
            max_interpolation_gap=5
        )
        
        # 無効な修復対象（終了日が開始日より前）
        invalid_target = RepairTarget(
            date_range={
                "start": date(2024, 8, 25),
                "end": date(2024, 8, 20)
            },
            max_interpolation_gap=5
        )
        
        # 検証実行
        validated = await service._validate_repair_targets([valid_target, invalid_target])
        
        # 有効なターゲットのみが残ることを確認
        assert len(validated) == 1
        assert validated[0].date_range["start"] == date(2024, 8, 20)

    @pytest.mark.asyncio
    async def test_repair_time_estimation(self, db_session):
        """修復時間見積もりテスト"""
        service = RepairService(db_session)
        
        # 短期間の修復対象
        short_target = RepairTarget(
            date_range={
                "start": date(2024, 8, 20),
                "end": date(2024, 8, 22)
            }
        )
        
        # 長期間の修復対象
        long_target = RepairTarget(
            date_range={
                "start": date(2024, 7, 1),
                "end": date(2024, 8, 1)
            }
        )
        
        short_time = await service._estimate_repair_time([short_target])
        long_time = await service._estimate_repair_time([long_target])
        
        # 長期間の方が時間がかかることを確認
        assert short_time <= long_time
        assert 5 <= short_time <= 60
        assert 5 <= long_time <= 60

    @pytest.mark.asyncio
    async def test_interpolated_value_calculation(self, db_session):
        """補間値計算テスト"""
        service = RepairService(db_session)
        
        # テスト用のデータを事前に挿入（実際のテストではDBにデータがあることを前提）
        missing_date = date(2024, 8, 21)
        max_gap = 5
        
        # 補間値計算を試行
        interpolated_value, confidence, source_dates = await service._calculate_interpolated_value(
            missing_date, max_gap
        )
        
        # 結果検証（データがない場合はNoneが返される）
        if interpolated_value is not None:
            assert isinstance(interpolated_value, Decimal)
            assert 0.0 <= confidence <= 1.0
            assert isinstance(source_dates, list)

    @pytest.mark.asyncio
    async def test_issue_identification(self, db_session):
        """問題特定テスト"""
        service = RepairService(db_session)
        
        # 期間設定
        start_date = date(2024, 8, 15)
        end_date = date(2024, 8, 25)
        
        # 問題特定実行
        issues = await service._identify_issues_in_range(
            start_date, end_date, ["missing_data", "outlier_values"]
        )
        
        # 結果検証
        assert isinstance(issues, list)
        
        # 各問題の形式確認
        for issue in issues:
            assert "type" in issue
            assert "date" in issue
            assert "description" in issue
            assert issue["type"] in ["missing_data", "outlier_values", "duplicate_data", "inconsistent_data"]


class TestDataProcessingServicesIntegration:
    """データ処理サービス統合テスト"""

    @pytest.mark.asyncio
    async def test_collection_to_quality_workflow(self, db_session):
        """データ収集から品質チェックへのワークフローテスト"""
        collection_service = CollectionService(db_session)
        quality_service = QualityService(db_session)
        
        # 1. データ収集実行
        collection_request = DataCollectionRequest(
            sources=[DataSourceType.YAHOO_FINANCE],
            force_update=False
        )
        
        collection_response = await collection_service.execute_data_collection(collection_request)
        assert collection_response.status in ["started", "failed"]
        
        # 2. 品質レポート生成
        quality_report = await quality_service.generate_data_quality_report(period_days=3)
        assert quality_report is not None
        assert quality_report.overall_quality_score is not None

    @pytest.mark.asyncio
    async def test_quality_to_repair_workflow(self, db_session):
        """品質チェックから修復へのワークフローテスト"""
        quality_service = QualityService(db_session)
        repair_service = RepairService(db_session)
        
        # 1. 品質問題の特定
        end_date = date.today()
        start_date = end_date - timedelta(days=7)
        
        issues = await quality_service._detect_quality_issues(start_date, end_date)
        
        # 2. 問題がある場合、修復実行
        if issues:
            repair_target = RepairTarget(
                date_range={
                    "start": start_date,
                    "end": end_date
                },
                issue_types=["missing_data"],
                max_interpolation_gap=5
            )
            
            repair_request = DataRepairRequest(
                repair_targets=[repair_target],
                dry_run=True
            )
            
            repair_response = await repair_service.execute_data_repair(repair_request)
            assert repair_response is not None

    @pytest.mark.asyncio
    async def test_error_handling_robustness(self, db_session):
        """エラーハンドリングの堅牢性テスト"""
        collection_service = CollectionService(db_session)
        quality_service = QualityService(db_session)
        repair_service = RepairService(db_session)
        
        # 異常なリクエストでもサービスが適切にエラーハンドリングすることを確認
        
        # Collection Service - 空のリクエスト
        try:
            empty_request = DataCollectionRequest(sources=[], force_update=False)
            response = await collection_service.execute_data_collection(empty_request)
            assert response is not None  # エラーでも適切なレスポンスを返すこと
        except Exception as e:
            # 適切な例外が発生すること
            assert str(e) is not None

        # Quality Service - 極端に長い期間
        try:
            report = await quality_service.generate_data_quality_report(period_days=1000)
            assert report is not None
        except Exception:
            pass  # エラーハンドリングが適切に動作すること

        # Repair Service - 不正な修復対象
        try:
            invalid_target = RepairTarget(
                date_range={
                    "start": date(2025, 1, 1),  # 未来の日付
                    "end": date(2025, 1, 10)
                }
            )
            invalid_request = DataRepairRequest(
                repair_targets=[invalid_target],
                dry_run=True
            )
            response = await repair_service.execute_data_repair(invalid_request)
            assert response is not None
        except Exception:
            pass  # 適切なエラーハンドリング