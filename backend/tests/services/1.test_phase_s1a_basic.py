"""
Forex Prediction System - Phase S-1a Unit Tests
===============================================

Phase S-1a基本サービス実装テスト
- rates_service.py
- data_service.py  
- sources_service.py

依存関係: なし（いつでも実行可能）
実行タイミング: 並列実行可能
"""

import pytest
import asyncio
from datetime import datetime, date, timedelta
from decimal import Decimal
from unittest.mock import Mock, AsyncMock, patch
from sqlalchemy.orm import Session

# テスト対象のインポート
from app.services.rates_service import RatesService
from app.services.data_service import DataService
from app.services.sources_service import SourcesService
from app.models import ExchangeRate, DataSource, DataSourceType, DataSourceStatus
from app.schemas.rates_minimal import CurrentRateResponse
from app.schemas.data import DataStatusResponse
from app.schemas.sources import SourcesStatusResponse


class TestRatesService:
    """現在レート取得サービステスト（1.1: /api/rates/current）"""

    def setup_method(self):
        """テストセットアップ"""
        self.mock_db = Mock(spec=Session)
        self.rates_service = RatesService(self.mock_db)

    @pytest.mark.asyncio
    async def test_get_current_rate_success(self):
        """正常ケース：現在レート取得成功"""
        # データベースから最新レートを取得する場合のモック
        mock_rate = ExchangeRate(
            id=1,
            date=date.today(),
            close_rate=Decimal("150.25"),
            open_rate=Decimal("149.80"),
            high_rate=Decimal("150.45"),
            low_rate=Decimal("149.55"),
            volume=125000000,
            source=DataSourceType.YAHOO_FINANCE,
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
        
        # 24時間前のレート
        mock_previous_rate = ExchangeRate(
            id=2,
            date=date.today() - timedelta(days=1),
            close_rate=Decimal("149.00"),
            source=DataSourceType.YAHOO_FINANCE,
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
        
        # データベースクエリのモック設定
        self.mock_db.execute.return_value.scalar_one_or_none.side_effect = [
            mock_rate,      # 最新レート
            mock_previous_rate  # 24時間前のレート
        ]
        
        # テスト実行
        result = await self.rates_service.get_current_rate()
        
        # 検証
        assert isinstance(result, CurrentRateResponse)
        assert result.rate == 150.25
        assert result.change_24h == 1.25  # 150.25 - 149.00
        assert result.change_percentage_24h > 0
        assert result.open_rate == 149.80
        assert result.high_rate == 150.45
        assert result.low_rate == 149.55
        assert result.volume == 125000000
        assert result.source == "yahoo_finance"
        assert isinstance(result.is_market_open, bool)
        assert isinstance(result.timestamp, datetime)

    @pytest.mark.asyncio
    async def test_get_current_rate_no_data_fallback(self):
        """エラーケース：データなし時のフォールバック"""
        # データベースにデータがない場合
        self.mock_db.execute.return_value.scalar_one_or_none.return_value = None
        
        # テスト実行
        result = await self.rates_service.get_current_rate()
        
        # フォールバックデータの検証
        assert isinstance(result, CurrentRateResponse)
        assert result.rate == 150.25  # フォールバック値
        assert result.change_24h == 0.0
        assert result.change_percentage_24h == 0.0
        assert result.source == "fallback"

    @pytest.mark.asyncio
    async def test_get_current_rate_database_error(self):
        """エラーケース：データベースエラー時のフォールバック"""
        # データベースエラーをシミュレート
        self.mock_db.execute.side_effect = Exception("Database connection error")
        
        # テスト実行
        result = await self.rates_service.get_current_rate()
        
        # エラー時フォールバックの検証
        assert isinstance(result, CurrentRateResponse)
        assert result.source == "error_fallback"

    def test_is_market_open_weekday(self):
        """市場開場判定：平日テスト"""
        # 平日の時刻をテスト（月曜日 10:00）
        monday_10am = datetime(2024, 8, 19, 10, 0, 0)  # 2024年8月19日は月曜日
        result = self.rates_service._is_market_open(monday_10am)
        assert result is True

    def test_is_market_open_weekend(self):
        """市場開場判定：週末テスト"""
        # 土曜日の時刻をテスト
        saturday = datetime(2024, 8, 17, 10, 0, 0)  # 2024年8月17日は土曜日
        result = self.rates_service._is_market_open(saturday)
        assert result is False

    def test_is_rate_stale_fresh_data(self):
        """レートデータ新鮮度判定：新しいデータ"""
        fresh_rate = ExchangeRate(
            date=date.today(),
            updated_at=datetime.now() - timedelta(hours=1)  # 1時間前
        )
        result = self.rates_service._is_rate_stale(fresh_rate)
        assert result is False

    def test_is_rate_stale_old_data(self):
        """レートデータ新鮮度判定：古いデータ"""
        stale_rate = ExchangeRate(
            date=date.today() - timedelta(days=1),  # 昨日のデータ
            updated_at=datetime.now() - timedelta(hours=8)  # 8時間前
        )
        result = self.rates_service._is_rate_stale(stale_rate)
        assert result is True


class TestDataService:
    """データ収集状況サービステスト（4.1: /api/data/status）"""

    def setup_method(self):
        """テストセットアップ"""
        self.mock_db = Mock(spec=Session)
        self.data_service = DataService(self.mock_db)

    @pytest.mark.asyncio
    async def test_get_data_status_success(self):
        """正常ケース：データ状況取得成功"""
        # データベースクエリの結果をモック
        self.mock_db.execute.return_value.scalar.side_effect = [
            8500,  # 実際のデータ件数
            30,    # 欠損データ件数
            15     # 補間データ件数
        ]
        
        # 日付のクエリ結果をモック
        earliest_date = date(1990, 1, 1)
        latest_date = date.today() - timedelta(days=1)
        last_update = datetime.now() - timedelta(hours=6)
        
        self.mock_db.execute.return_value.scalar.side_effect = [
            8500, 30, 15,  # カバレッジ計算用
            earliest_date, latest_date, last_update  # 日付情報
        ]
        
        # テスト実行
        result = await self.data_service.get_data_status()
        
        # 検証
        assert isinstance(result, DataStatusResponse)
        assert result.coverage is not None
        assert result.quality is not None
        assert result.schedule is not None
        assert result.system_health in ["healthy", "warning", "critical"]
        assert isinstance(result.active_issues, list)
        assert isinstance(result.status_generated_at, datetime)

    @pytest.mark.asyncio  
    async def test_get_data_status_database_error(self):
        """エラーケース：データベースエラー時のフォールバック"""
        # データベースエラーをシミュレート
        self.mock_db.execute.side_effect = Exception("Database error")
        
        # テスト実行
        result = await self.data_service.get_data_status()
        
        # フォールバックデータの検証
        assert isinstance(result, DataStatusResponse)
        assert result.system_health == "warning"
        assert "Data status service temporarily unavailable" in result.active_issues

    @pytest.mark.asyncio
    async def test_calculate_data_coverage(self):
        """データカバレッジ計算のテスト"""
        # データベースクエリ結果のモック
        self.mock_db.execute.return_value.scalar.side_effect = [
            8500,  # 実データ件数
            30,    # 欠損データ件数
            15     # 補間データ件数
        ]
        self.mock_db.execute.return_value.scalar.side_effect = [
            date(1990, 1, 1),  # 最古データ
            date.today() - timedelta(days=1),  # 最新データ
            datetime.now() - timedelta(hours=6)  # 最終更新
        ]
        
        # テスト実行
        coverage = await self.data_service._calculate_data_coverage()
        
        # 検証
        assert coverage.actual_data_days >= 0
        assert 0.0 <= coverage.coverage_rate <= 1.0
        assert coverage.earliest_date <= coverage.latest_date


class TestSourcesService:
    """データソース稼働状況サービステスト（6.1: /api/sources/status, 6.4: /api/sources/health）"""

    def setup_method(self):
        """テストセットアップ"""
        self.mock_db = Mock(spec=Session)
        self.sources_service = SourcesService(self.mock_db)

    @pytest.mark.asyncio
    async def test_get_sources_status_with_data(self):
        """正常ケース：データソース状況取得（データベースにデータあり）"""
        # モックデータソース
        mock_source = DataSource(
            id=1,
            name="Yahoo Finance",
            source_type=DataSourceType.YAHOO_FINANCE,
            status=DataSourceStatus.ACTIVE,
            url="https://finance.yahoo.com/quote/USDJPY=X/",
            priority=1,
            success_rate=Decimal("0.95"),
            avg_response_time=1200,
            daily_request_count=145,
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
        
        # データベースクエリ結果をモック
        self.mock_db.execute.return_value.scalars.return_value.all.return_value = [mock_source]
        
        # テスト実行
        result = await self.sources_service.get_sources_status()
        
        # 検証
        assert isinstance(result, SourcesStatusResponse)
        assert len(result.sources) > 0
        assert result.summary.total_sources >= 1
        assert isinstance(result.timestamp, datetime)

    @pytest.mark.asyncio
    async def test_get_sources_status_no_data_initialization(self):
        """正常ケース：データソース状況取得（データベースにデータなし→初期化）"""
        # データベースにデータがない場合
        self.mock_db.execute.return_value.scalars.return_value.all.return_value = []
        
        # テスト実行
        result = await self.sources_service.get_sources_status()
        
        # 初期化データの検証
        assert isinstance(result, SourcesStatusResponse)
        assert len(result.sources) > 0  # 初期化されたソース
        assert result.summary.total_sources > 0

    @pytest.mark.asyncio
    async def test_get_sources_status_database_error(self):
        """エラーケース：データベースエラー時のフォールバック"""
        # データベースエラーをシミュレート
        self.mock_db.execute.side_effect = Exception("Database error")
        
        # テスト実行
        result = await self.sources_service.get_sources_status()
        
        # フォールバックデータの検証
        assert isinstance(result, SourcesStatusResponse)
        assert len(result.sources) > 0  # フォールバックデータ

    @pytest.mark.asyncio
    async def test_check_sources_health_success(self):
        """正常ケース：ヘルスチェック実行成功"""
        # モックデータソース
        mock_source = DataSource(
            id=1,
            name="Yahoo Finance",
            source_type=DataSourceType.YAHOO_FINANCE,
            status=DataSourceStatus.ACTIVE,
            url="https://finance.yahoo.com/quote/USDJPY=X/",
            priority=1
        )
        
        # データベースクエリ結果をモック
        self.mock_db.execute.return_value.scalars.return_value.all.return_value = [mock_source]
        
        # HTTP通信のモック（aiohttp）
        with patch('aiohttp.ClientSession') as mock_session:
            mock_response = AsyncMock()
            mock_response.status = 200
            mock_session.return_value.__aenter__.return_value.head.return_value.__aenter__.return_value = mock_response
            
            # テスト実行
            result = await self.sources_service.check_sources_health()
        
        # 検証
        assert isinstance(result.summary.total_checked, int)
        assert len(result.health_checks) > 0
        assert isinstance(result.timestamp, datetime)
        assert isinstance(result.next_check_at, datetime)

    @pytest.mark.asyncio
    async def test_check_sources_health_no_sources(self):
        """正常ケース：ソースなし時のデフォルトヘルスチェック"""
        # データベースにソースがない場合
        self.mock_db.execute.return_value.scalars.return_value.all.return_value = []
        
        # テスト実行
        result = await self.sources_service.check_sources_health()
        
        # デフォルトヘルスチェックの検証
        assert len(result.health_checks) > 0
        assert result.summary.total_checked > 0

    def test_convert_to_enum(self):
        """型変換メソッドのテスト"""
        # DataSourceType → DataSourceTypeEnum変換
        result = self.sources_service._convert_to_enum(DataSourceType.YAHOO_FINANCE)
        from app.schemas.sources import DataSourceTypeEnum
        assert result == DataSourceTypeEnum.YAHOO_FINANCE

    def test_convert_status_to_enum(self):
        """ステータス型変換メソッドのテスト"""
        # DataSourceStatus → DataSourceStatusEnum変換
        result = self.sources_service._convert_status_to_enum(DataSourceStatus.ACTIVE)
        from app.schemas.sources import DataSourceStatusEnum
        assert result == DataSourceStatusEnum.ACTIVE


class TestIntegration:
    """統合テスト（Phase S-1a全体）"""

    def setup_method(self):
        """テストセットアップ"""
        self.mock_db = Mock(spec=Session)

    @pytest.mark.asyncio
    async def test_all_services_instantiation(self):
        """全サービスクラスのインスタンス化テスト"""
        # 全てのサービスが正常にインスタンス化できることを確認
        rates_service = RatesService(self.mock_db)
        data_service = DataService(self.mock_db)
        sources_service = SourcesService(self.mock_db)
        
        # インスタンスの型確認
        assert isinstance(rates_service, RatesService)
        assert isinstance(data_service, DataService)
        assert isinstance(sources_service, SourcesService)
        
        # データベースセッションが正しく設定されていることを確認
        assert rates_service.db == self.mock_db
        assert data_service.db == self.mock_db
        assert sources_service.db == self.mock_db

    def test_service_method_signatures(self):
        """サービスメソッドのシグネチャ確認"""
        # RatesServiceメソッド確認
        rates_service = RatesService(self.mock_db)
        assert hasattr(rates_service, 'get_current_rate')
        assert callable(rates_service.get_current_rate)
        
        # DataServiceメソッド確認
        data_service = DataService(self.mock_db)
        assert hasattr(data_service, 'get_data_status')
        assert callable(data_service.get_data_status)
        
        # SourcesServiceメソッド確認
        sources_service = SourcesService(self.mock_db)
        assert hasattr(sources_service, 'get_sources_status')
        assert hasattr(sources_service, 'check_sources_health')
        assert callable(sources_service.get_sources_status)
        assert callable(sources_service.check_sources_health)


# テスト実行設定
if __name__ == "__main__":
    # 個別テスト実行用
    pytest.main([__file__, "-v", "--tb=short"])