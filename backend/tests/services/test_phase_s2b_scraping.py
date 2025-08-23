"""
Tests for Phase S-2b: Data Sources Operation Services - Scraping Service
スクレイピングサービス単体テスト

Phase S-2b-1: Scraping Service
- エンドポイント 6.2: /api/sources/scrape - Webスクレイピング実行
"""

import pytest
import tempfile
import os
from datetime import datetime, timedelta
from typing import List, Dict, Any
from unittest.mock import patch

from app.services.scraping_service import ScrapingService
from app.models import ExchangeRate, DataSourceType
from app.schemas.sources import ScrapeResultItem


@pytest.mark.asyncio
async def test_scrape_yahoo_finance_usdjpy_basic(db_session):
    """
    Yahoo Finance USD/JPY スクレイピング基本機能テスト
    """
    service = ScrapingService(db_session)
    
    # テスト用URL
    test_urls = ["https://finance.yahoo.com/quote/USDJPY=X/"]
    
    # スクレイピング実行
    results = await service.scrape_yahoo_finance_usdjpy(
        target_urls=test_urls,
        date_range_start=None,
        date_range_end=None
    )
    
    # 結果検証
    assert isinstance(results, list)
    assert len(results) == 1
    
    result = results[0]
    assert isinstance(result, ScrapeResultItem)
    assert result.url == test_urls[0]
    assert isinstance(result.success, bool)
    assert isinstance(result.records_extracted, int)
    assert result.records_extracted >= 0
    assert isinstance(result.response_time_ms, int)
    assert result.extracted_at is not None


@pytest.mark.asyncio
async def test_scrape_multiple_urls_parallel(db_session):
    """
    複数URL並列スクレイピングテスト
    """
    service = ScrapingService(db_session)
    
    # 複数のテスト用URL
    test_urls = [
        "https://finance.yahoo.com/quote/USDJPY=X/",
        "https://example.com/forex/usdjpy",
        "https://invalid-url-for-testing.com/data"
    ]
    
    # 並列スクレイピング実行
    results = await service.scrape_yahoo_finance_usdjpy(test_urls)
    
    # 結果検証
    assert len(results) == 3
    
    success_count = sum(1 for r in results if r.success)
    failed_count = sum(1 for r in results if not r.success)
    
    # すべてのURLに対して結果が返される
    assert success_count + failed_count == 3
    
    # 各結果の妥当性確認
    for i, result in enumerate(results):
        assert result.url == test_urls[i]
        if result.success:
            assert result.records_extracted > 0
            assert result.error_message is None
        else:
            assert result.records_extracted == 0
            assert result.error_message is not None


@pytest.mark.asyncio
async def test_scrape_with_date_range_filter(db_session):
    """
    日付範囲フィルタを使ったスクレイピングテスト
    """
    service = ScrapingService(db_session)
    
    # 日付範囲設定
    start_date = datetime.now() - timedelta(days=7)
    end_date = datetime.now() - timedelta(days=1)
    
    test_urls = ["https://finance.yahoo.com/quote/USDJPY=X/"]
    
    results = await service.scrape_yahoo_finance_usdjpy(
        target_urls=test_urls,
        date_range_start=start_date,
        date_range_end=end_date
    )
    
    assert len(results) == 1
    result = results[0]
    
    # データが取得できた場合、日付範囲内のデータかチェック
    if result.success and result.data_preview:
        for data_item in result.data_preview:
            if 'date' in data_item:
                data_date = datetime.strptime(data_item['date'], '%Y-%m-%d')
                assert start_date.date() <= data_date.date() <= end_date.date()


@pytest.mark.asyncio
async def test_save_scraped_data_to_database(db_session):
    """
    スクレイピングデータのデータベース保存テスト
    """
    service = ScrapingService(db_session)
    
    # テスト用スクレイピングデータ
    test_data = [
        {
            "date": "2024-01-15",
            "open_rate": 148.25,
            "high_rate": 149.15,
            "low_rate": 147.80,
            "close_rate": 148.95,
            "volume": 125000,
            "source": "yahoo_finance"
        },
        {
            "date": "2024-01-16",
            "open_rate": 148.95,
            "high_rate": 149.80,
            "low_rate": 148.30,
            "close_rate": 149.45,
            "volume": 132000,
            "source": "yahoo_finance"
        }
    ]
    
    # データベース保存実行
    saved_count = await service.save_scraped_data(test_data)
    
    # 結果検証
    assert saved_count == len(test_data)
    
    # データベースからデータを確認
    from sqlalchemy import select
    
    for data_item in test_data:
        expected_date = datetime.strptime(data_item['date'], '%Y-%m-%d').date()
        
        stmt = select(ExchangeRate).where(ExchangeRate.date == expected_date)
        result = await db_session.execute(stmt)
        saved_record = result.scalar_one_or_none()
        
        assert saved_record is not None
        assert float(saved_record.close_rate) == data_item['close_rate']
        assert saved_record.source == DataSourceType.SCRAPING


@pytest.mark.asyncio
async def test_validate_scraped_data_quality(db_session):
    """
    スクレイピングデータ品質検証テスト
    """
    service = ScrapingService(db_session)
    
    # 正常データと異常データの混合
    test_data = [
        {
            "date": "2024-01-15",
            "close_rate": 148.95,
            "volume": 125000
        },
        {
            "date": "invalid-date",
            "close_rate": 149.45,
            "volume": 132000
        },
        {
            "date": "2024-01-17",
            "close_rate": -1.0,  # 無効なレート値
            "volume": 145000
        },
        {
            "date": "2024-01-18",
            "close_rate": None,  # 欠損値
            "volume": 150000
        }
    ]
    
    # データ検証実行
    validation_result = await service.validate_scraped_data(test_data)
    
    # 検証結果の確認
    assert validation_result["total_records"] == 4
    assert validation_result["valid_records"] >= 1
    assert validation_result["invalid_records"] >= 1
    assert len(validation_result["validation_errors"]) > 0
    
    # 日付範囲が設定されているか確認
    if validation_result["date_range"]["start"]:
        assert validation_result["date_range"]["end"] is not None


@pytest.mark.asyncio
async def test_generate_sample_forex_data(db_session):
    """
    サンプル為替データ生成機能テスト
    """
    service = ScrapingService(db_session)
    
    # サンプルデータ生成
    sample_data = service._generate_sample_forex_data(5)
    
    # 結果検証
    assert len(sample_data) == 5
    
    for data_item in sample_data:
        # 必須フィールド存在確認
        assert "date" in data_item
        assert "close_rate" in data_item
        
        # データ型確認
        assert isinstance(data_item["close_rate"], float)
        assert data_item["close_rate"] > 0
        
        # 日付フォーマット確認
        datetime.strptime(data_item["date"], '%Y-%m-%d')
        
        # OHLC整合性確認（値が存在する場合）
        if all(k in data_item for k in ["open_rate", "high_rate", "low_rate", "close_rate"]):
            o, h, l, c = [data_item[k] for k in ["open_rate", "high_rate", "low_rate", "close_rate"]]
            assert h >= max(o, l, c), f"High should be >= other rates: {data_item}"
            assert l <= min(o, h, c), f"Low should be <= other rates: {data_item}"


@pytest.mark.asyncio 
async def test_scraping_error_handling(db_session):
    """
    スクレイピングエラーハンドリングテスト
    """
    service = ScrapingService(db_session)
    
    # 無効なURLでのテスト
    invalid_urls = [
        "https://nonexistent-domain-for-testing-12345.com/",
        "invalid-url-format",
        ""
    ]
    
    results = await service.scrape_yahoo_finance_usdjpy(invalid_urls)
    
    # エラーハンドリング確認
    assert len(results) == len(invalid_urls)
    
    for i, result in enumerate(results):
        if invalid_urls[i]:  # 空文字列以外
            assert result.url == invalid_urls[i]
        assert not result.success
        assert result.records_extracted == 0
        assert result.error_message is not None
        assert result.response_time_ms > 0


@pytest.mark.asyncio
async def test_duplicate_data_handling(db_session):
    """
    重複データ処理テスト
    """
    service = ScrapingService(db_session)
    
    # 同じ日付のデータを2回保存
    test_data = [
        {
            "date": "2024-01-20",
            "close_rate": 148.50,
            "volume": 100000
        }
    ]
    
    # 1回目の保存
    saved_count_1 = await service.save_scraped_data(test_data)
    assert saved_count_1 == 1
    
    # 同じデータをもう一度保存（更新されるべき）
    updated_data = [
        {
            "date": "2024-01-20",
            "close_rate": 149.00,  # 異なるレート
            "volume": 110000
        }
    ]
    
    saved_count_2 = await service.save_scraped_data(updated_data)
    assert saved_count_2 == 1
    
    # データベースから確認
    from sqlalchemy import select
    expected_date = datetime.strptime("2024-01-20", '%Y-%m-%d').date()
    
    stmt = select(ExchangeRate).where(ExchangeRate.date == expected_date)
    result = await db_session.execute(stmt)
    updated_record = result.scalar_one_or_none()
    
    # 更新されたデータが保存されていることを確認
    assert updated_record is not None
    assert float(updated_record.close_rate) == 149.00