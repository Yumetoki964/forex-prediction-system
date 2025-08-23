"""
Data Sources Service Unit Tests

データソース管理サービスの単体テスト
- get_sources_status のテスト
- check_sources_health のテスト
- CRUD操作のテスト
"""

import pytest
import asyncio
from datetime import datetime, timedelta
from decimal import Decimal
from unittest.mock import AsyncMock, patch, MagicMock
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

from app.services.sources_service import SourcesService
from app.models import DataSource
from app.schemas.sources import (
    DataSourceTypeEnum,
    DataSourceStatusEnum,
    HealthStatusEnum
)


class TestSourcesService:
    """データソースサービスのテストクラス"""
    
    @pytest.fixture
    async def mock_db_session(self):
        """モックデータベースセッション"""
        session = AsyncMock(spec=AsyncSession)
        return session
    
    @pytest.fixture
    def sources_service(self, mock_db_session):
        """SourcesServiceインスタンス"""
        return SourcesService(mock_db_session)
    
    @pytest.fixture
    def sample_data_sources(self):
        """サンプルデータソース"""
        current_time = datetime.now()
        return [
            DataSource(
                id=1,
                name="Yahoo Finance",
                source_type=DataSourceTypeEnum.YAHOO_FINANCE,
                status=DataSourceStatusEnum.ACTIVE,
                priority=1,
                success_rate=Decimal('0.95'),
                avg_response_time=1200,
                last_success_at=current_time - timedelta(minutes=5),
                last_failure_at=None,
                failure_count=0,
                daily_request_count=145,
                rate_limit_requests=None,
                rate_limit_period=None,
                last_request_at=current_time - timedelta(minutes=5),
                created_at=current_time - timedelta(days=30),
                updated_at=current_time
            ),
            DataSource(
                id=2,
                name="BOJ CSV",
                source_type=DataSourceTypeEnum.BOJ_CSV,
                status=DataSourceStatusEnum.ACTIVE,
                priority=2,
                success_rate=Decimal('0.98'),
                avg_response_time=2500,
                last_success_at=current_time - timedelta(hours=1),
                last_failure_at=None,
                failure_count=0,
                daily_request_count=12,
                rate_limit_requests=None,
                rate_limit_period=None,
                last_request_at=current_time - timedelta(hours=1),
                created_at=current_time - timedelta(days=60),
                updated_at=current_time
            ),
            DataSource(
                id=3,
                name="Alpha Vantage",
                source_type=DataSourceTypeEnum.ALPHA_VANTAGE,
                status=DataSourceStatusEnum.ACTIVE,
                priority=3,
                success_rate=Decimal('0.88'),
                avg_response_time=3200,
                last_success_at=current_time - timedelta(minutes=30),
                last_failure_at=current_time - timedelta(hours=2),
                failure_count=2,
                daily_request_count=89,
                rate_limit_requests=500,
                rate_limit_period=86400,
                last_request_at=current_time - timedelta(minutes=30),
                created_at=current_time - timedelta(days=90),
                updated_at=current_time
            ),
            DataSource(
                id=4,
                name="Web Scraping Backup",
                source_type=DataSourceTypeEnum.SCRAPING,
                status=DataSourceStatusEnum.ERROR,
                priority=4,
                success_rate=Decimal('0.45'),
                avg_response_time=8500,
                last_success_at=current_time - timedelta(hours=6),
                last_failure_at=current_time - timedelta(minutes=15),
                failure_count=12,
                daily_request_count=25,
                rate_limit_requests=None,
                rate_limit_period=None,
                last_request_at=current_time - timedelta(minutes=15),
                created_at=current_time - timedelta(days=10),
                updated_at=current_time
            )
        ]
    
    @pytest.mark.asyncio
    async def test_get_sources_status_success(self, sources_service, mock_db_session, sample_data_sources):
        """データソース稼働状況取得の正常系テスト"""
        # モックの設定
        mock_result = MagicMock()
        mock_result.scalars.return_value.all.return_value = sample_data_sources
        mock_db_session.execute.return_value = mock_result
        
        # テスト実行
        response = await sources_service.get_sources_status()
        
        # 検証
        assert response is not None
        assert response.summary.total_sources == 4
        assert response.summary.active_sources == 3
        assert response.summary.error_sources == 1
        assert response.summary.maintenance_sources == 0
        assert len(response.sources) == 4
        
        # 平均成功率の検証
        expected_avg = (0.95 + 0.98 + 0.88 + 0.45) / 4
        assert abs(response.summary.average_success_rate - expected_avg) < 0.001
        
        # 個別ソースの検証
        yahoo_source = next((s for s in response.sources if s.name == "Yahoo Finance"), None)
        assert yahoo_source is not None
        assert yahoo_source.source_type == DataSourceTypeEnum.YAHOO_FINANCE
        assert yahoo_source.status == DataSourceStatusEnum.ACTIVE
        assert yahoo_source.success_rate == 0.95
    
    @pytest.mark.asyncio
    async def test_get_sources_status_empty_database(self, sources_service, mock_db_session):
        """データソースが存在しない場合のテスト"""
        # モックの設定（空のリスト）
        mock_result = MagicMock()
        mock_result.scalars.return_value.all.return_value = []
        mock_db_session.execute.return_value = mock_result
        
        # テスト実行
        response = await sources_service.get_sources_status()
        
        # 検証
        assert response is not None
        assert response.summary.total_sources == 0
        assert response.summary.active_sources == 0
        assert response.summary.average_success_rate == 0.0
        assert len(response.sources) == 0
    
    @pytest.mark.asyncio
    async def test_get_sources_status_database_error(self, sources_service, mock_db_session):
        """データベースエラーの場合のテスト"""
        # モックの設定（例外発生）
        mock_db_session.execute.side_effect = Exception("Database connection failed")
        
        # テスト実行と検証
        with pytest.raises(Exception) as exc_info:
            await sources_service.get_sources_status()
        
        assert "データソース稼働状況取得中にエラー" in str(exc_info.value)
    
    @pytest.mark.asyncio
    async def test_check_sources_health_success(self, sources_service, mock_db_session, sample_data_sources):
        """ヘルスチェックの正常系テスト"""
        # モックの設定
        mock_result = MagicMock()
        mock_result.scalars.return_value.all.return_value = sample_data_sources
        mock_db_session.execute.return_value = mock_result
        mock_db_session.commit.return_value = None
        
        # テスト実行
        response = await sources_service.check_sources_health()
        
        # 検証
        assert response is not None
        assert response.summary.total_checked == 4
        assert len(response.health_checks) == 4
        assert response.next_check_at > response.timestamp
        
        # ヘルスステータスの分布確認
        healthy_count = sum(1 for hc in response.health_checks if hc.health_status == HealthStatusEnum.HEALTHY)
        degraded_count = sum(1 for hc in response.health_checks if hc.health_status == HealthStatusEnum.DEGRADED)
        unhealthy_count = sum(1 for hc in response.health_checks if hc.health_status == HealthStatusEnum.UNHEALTHY)
        
        assert healthy_count + degraded_count + unhealthy_count == 4
        assert response.summary.healthy_count == healthy_count
        assert response.summary.degraded_count == degraded_count
        assert response.summary.unhealthy_count == unhealthy_count
    
    @pytest.mark.asyncio
    async def test_check_sources_health_with_exceptions(self, sources_service, mock_db_session, sample_data_sources):
        """ヘルスチェック中に例外が発生した場合のテスト"""
        # モックの設定
        mock_result = MagicMock()
        mock_result.scalars.return_value.all.return_value = sample_data_sources[:2]  # 2つのソースのみ
        mock_db_session.execute.return_value = mock_result
        mock_db_session.commit.return_value = None
        
        # 個別ヘルスチェックで例外発生をシミュレート
        with patch.object(sources_service, '_perform_health_check') as mock_health_check:
            # 1つ目は正常、2つ目は例外
            mock_health_check.side_effect = [
                MagicMock(health_status=HealthStatusEnum.HEALTHY),
                Exception("Connection timeout")
            ]
            
            # テスト実行
            response = await sources_service.check_sources_health()
            
            # 検証：例外が発生してもレスポンスは正常に作成される
            assert response is not None
            assert response.summary.total_checked == 2
            assert len(response.health_checks) == 2
            
            # UNKNOWNステータスで記録されることを確認
            unknown_checks = [hc for hc in response.health_checks if hc.health_status == HealthStatusEnum.UNKNOWN]
            assert len(unknown_checks) > 0
    
    @pytest.mark.asyncio
    async def test_perform_yahoo_finance_health_check(self, sources_service):
        """Yahoo Financeのヘルスチェック個別テスト"""
        sample_source = DataSource(
            id=1,
            name="Yahoo Finance",
            source_type=DataSourceTypeEnum.YAHOO_FINANCE,
            status=DataSourceStatusEnum.ACTIVE,
            priority=1
        )
        
        # モックの設定
        with patch.object(sources_service.db, 'execute') as mock_execute, \
             patch.object(sources_service.db, 'commit') as mock_commit:
            
            mock_execute.return_value = None
            mock_commit.return_value = None
            
            # テスト実行
            result = await sources_service._perform_health_check(sample_source)
            
            # 検証
            assert result is not None
            assert result.id == 1
            assert result.name == "Yahoo Finance"
            assert result.source_type == DataSourceTypeEnum.YAHOO_FINANCE
            assert result.connectivity in [True, False]
            assert result.data_availability in [True, False]
            assert isinstance(result.last_check_at, datetime)
    
    @pytest.mark.asyncio
    async def test_perform_alpha_vantage_health_check(self, sources_service):
        """Alpha Vantageのヘルスチェック個別テスト"""
        sample_source = DataSource(
            id=3,
            name="Alpha Vantage",
            source_type=DataSourceTypeEnum.ALPHA_VANTAGE,
            status=DataSourceStatusEnum.ACTIVE,
            priority=3
        )
        
        # モックの設定
        with patch.object(sources_service.db, 'execute') as mock_execute, \
             patch.object(sources_service.db, 'commit') as mock_commit:
            
            mock_execute.return_value = None
            mock_commit.return_value = None
            
            # テスト実行
            result = await sources_service._perform_health_check(sample_source)
            
            # 検証
            assert result is not None
            assert result.source_type == DataSourceTypeEnum.ALPHA_VANTAGE
            # Alpha Vantageはレート制限情報を含む可能性がある
            # rate_limit_statusの存在を確認（Noneでも可）
            assert hasattr(result, 'rate_limit_status')
    
    @pytest.mark.asyncio
    async def test_determine_health_status_logic(self, sources_service):
        """ヘルスステータス判定ロジックのテスト"""
        # HEALTHY: 接続可能、データ取得可能、エラーなし、高速レスポンス
        status = sources_service._determine_health_status(True, True, 1000, None)
        assert status == HealthStatusEnum.HEALTHY
        
        # DEGRADED: 接続可能だがレスポンス時間が遅い
        status = sources_service._determine_health_status(True, True, 6000, None)
        assert status == HealthStatusEnum.DEGRADED
        
        # DEGRADED: 接続可能だがエラーメッセージあり
        status = sources_service._determine_health_status(True, True, 2000, "Warning message")
        assert status == HealthStatusEnum.DEGRADED
        
        # UNHEALTHY: 接続不可
        status = sources_service._determine_health_status(False, True, None, None)
        assert status == HealthStatusEnum.UNHEALTHY
        
        # UNHEALTHY: データ取得不可
        status = sources_service._determine_health_status(True, False, 1000, None)
        assert status == HealthStatusEnum.UNHEALTHY
    
    @pytest.mark.asyncio
    async def test_get_all_sources(self, sources_service, mock_db_session, sample_data_sources):
        """全データソース取得のテスト"""
        # モックの設定
        mock_result = MagicMock()
        mock_result.scalars.return_value.all.return_value = sample_data_sources
        mock_db_session.execute.return_value = mock_result
        
        # テスト実行
        sources = await sources_service.get_all_sources()
        
        # 検証
        assert len(sources) == 4
        assert all(isinstance(source, DataSource) for source in sources)
        
        # ソート順序の確認（priorityの昇順）
        priorities = [source.priority for source in sources]
        assert priorities == sorted(priorities)
    
    @pytest.mark.asyncio
    async def test_get_source_by_id(self, sources_service, mock_db_session, sample_data_sources):
        """ID指定でのデータソース取得テスト"""
        # モックの設定
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = sample_data_sources[0]  # Yahoo Finance
        mock_db_session.execute.return_value = mock_result
        
        # テスト実行
        source = await sources_service.get_source_by_id(1)
        
        # 検証
        assert source is not None
        assert source.id == 1
        assert source.name == "Yahoo Finance"
        assert source.source_type == DataSourceTypeEnum.YAHOO_FINANCE
    
    @pytest.mark.asyncio
    async def test_get_source_by_id_not_found(self, sources_service, mock_db_session):
        """存在しないIDでの取得テスト"""
        # モックの設定（見つからない場合）
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = None
        mock_db_session.execute.return_value = mock_result
        
        # テスト実行
        source = await sources_service.get_source_by_id(999)
        
        # 検証
        assert source is None
    
    @pytest.mark.asyncio
    async def test_get_sources_by_type(self, sources_service, mock_db_session, sample_data_sources):
        """種別指定でのデータソース取得テスト"""
        # Yahoo Financeタイプのソースのみを返すモック設定
        yahoo_sources = [ds for ds in sample_data_sources if ds.source_type == DataSourceTypeEnum.YAHOO_FINANCE]
        
        mock_result = MagicMock()
        mock_result.scalars.return_value.all.return_value = yahoo_sources
        mock_db_session.execute.return_value = mock_result
        
        # テスト実行
        sources = await sources_service.get_sources_by_type(DataSourceTypeEnum.YAHOO_FINANCE)
        
        # 検証
        assert len(sources) == 1
        assert sources[0].source_type == DataSourceTypeEnum.YAHOO_FINANCE
        assert sources[0].name == "Yahoo Finance"
    
    @pytest.mark.asyncio
    async def test_health_check_response_time_measurement(self, sources_service):
        """ヘルスチェックのレスポンス時間測定テスト"""
        # 各データソース種別のヘルスチェック実行時間を測定
        test_sources = [
            DataSource(id=1, source_type=DataSourceTypeEnum.YAHOO_FINANCE, name="Test Yahoo"),
            DataSource(id=2, source_type=DataSourceTypeEnum.BOJ_CSV, name="Test BOJ"),
            DataSource(id=3, source_type=DataSourceTypeEnum.ALPHA_VANTAGE, name="Test Alpha"),
            DataSource(id=4, source_type=DataSourceTypeEnum.SCRAPING, name="Test Scraping"),
        ]
        
        # モックの設定
        with patch.object(sources_service.db, 'execute') as mock_execute, \
             patch.object(sources_service.db, 'commit') as mock_commit:
            
            mock_execute.return_value = None
            mock_commit.return_value = None
            
            for source in test_sources:
                start_time = datetime.now()
                result = await sources_service._perform_health_check(source)
                end_time = datetime.now()
                
                # レスポンス時間が適切に記録されていることを確認
                assert result.response_time_ms is None or result.response_time_ms >= 0
                
                # 実際の実行時間と記録された時間の整合性確認
                actual_duration = (end_time - start_time).total_seconds() * 1000
                # ヘルスチェック実行は1秒以内に完了すべき
                assert actual_duration < 1000


if __name__ == "__main__":
    # テスト実行
    pytest.main([__file__, "-v"])