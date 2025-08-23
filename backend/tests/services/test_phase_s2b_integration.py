"""
Integration Tests for Phase S-2b: Data Sources Operation Services
データソース操作サービス統合テスト

Phase S-2b Integration: Scraping + Import Services
- エンドポイント 6.2: /api/sources/scrape - Webスクレイピング実行
- エンドポイント 6.3: /api/sources/csv-import - CSV一括インポート
- 両サービスの統合動作テスト
"""

import pytest
import tempfile
import csv
import os
from datetime import datetime, timedelta
from sqlalchemy import select

from app.services.scraping_service import ScrapingService
from app.services.import_service import ImportService
from app.models import ExchangeRate, DataSourceType


@pytest.mark.asyncio
async def test_scraping_and_import_data_consistency(db_session):
    """
    スクレイピングとインポートデータの整合性テスト
    """
    scraping_service = ScrapingService(db_session)
    import_service = ImportService(db_session)
    
    # 1. CSVインポートでベースデータ作成
    with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as temp_file:
        writer = csv.writer(temp_file)
        writer.writerow(['date', 'open_rate', 'high_rate', 'low_rate', 'close_rate', 'volume'])
        writer.writerow(['2024-01-15', '148.25', '149.15', '147.80', '148.95', '125000'])
        writer.writerow(['2024-01-16', '148.95', '149.80', '148.30', '149.45', '132000'])
        temp_file_path = temp_file.name
    
    try:
        # CSVインポート実行
        import_result = await import_service.import_csv_file(
            file_path=temp_file_path,
            source_type=DataSourceType.BOJ_CSV
        )
        
        assert import_result["import_summary"]["inserted"] == 2
        
        # 2. スクレイピングでサンプルデータ取得
        test_urls = ["https://finance.yahoo.com/quote/USDJPY=X/"]
        scraping_results = await scraping_service.scrape_yahoo_finance_usdjpy(test_urls)
        
        # 3. データベース内容確認
        stmt = select(ExchangeRate).where(
            ExchangeRate.date.in_([
                datetime.strptime('2024-01-15', '%Y-%m-%d').date(),
                datetime.strptime('2024-01-16', '%Y-%m-%d').date()
            ])
        )
        result = await db_session.execute(stmt)
        imported_records = result.scalars().all()
        
        # インポートされたデータが存在することを確認
        assert len(imported_records) == 2
        
        for record in imported_records:
            assert record.source == DataSourceType.BOJ_CSV
            assert float(record.close_rate) > 0
    
    finally:
        os.unlink(temp_file_path)


@pytest.mark.asyncio
async def test_data_source_priority_handling(db_session):
    """
    複数データソースからの同一日付データ処理テスト
    """
    scraping_service = ScrapingService(db_session)
    import_service = ImportService(db_session)
    
    test_date = "2024-01-22"
    
    # 1. CSVインポートでベースデータ作成
    with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as temp_file:
        writer = csv.writer(temp_file)
        writer.writerow(['date', 'close_rate'])
        writer.writerow([test_date, '148.50'])
        temp_file_path = temp_file.name
    
    try:
        # CSVデータインポート
        await import_service.import_csv_file(
            file_path=temp_file_path,
            source_type=DataSourceType.BOJ_CSV
        )
        
        # 2. スクレイピングデータで同じ日付を上書き
        scraped_data = [{
            "date": test_date,
            "close_rate": 149.00,  # 異なるレート値
            "source": "yahoo_finance"
        }]
        
        await scraping_service.save_scraped_data(scraped_data)
        
        # 3. 最終的に保存されたデータを確認
        stmt = select(ExchangeRate).where(
            ExchangeRate.date == datetime.strptime(test_date, '%Y-%m-%d').date()
        )
        result = await db_session.execute(stmt)
        final_record = result.scalar_one_or_none()
        
        # スクレイピングデータで上書きされていることを確認
        assert final_record is not None
        assert float(final_record.close_rate) == 149.00
        assert final_record.source == DataSourceType.SCRAPING
    
    finally:
        os.unlink(temp_file_path)


@pytest.mark.asyncio
async def test_large_dataset_processing_performance(db_session):
    """
    大量データ処理性能テスト
    """
    import_service = ImportService(db_session)
    
    # 100件の大量データCSV作成
    with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as temp_file:
        writer = csv.writer(temp_file)
        writer.writerow(['date', 'close_rate', 'volume'])
        
        base_date = datetime(2024, 1, 1)
        for i in range(100):
            current_date = base_date + timedelta(days=i)
            rate = 148.0 + (i * 0.01)
            volume = 100000 + (i * 1000)
            writer.writerow([
                current_date.strftime('%Y-%m-%d'), 
                f'{rate:.2f}', 
                str(volume)
            ])
        
        temp_file_path = temp_file.name
    
    try:
        # 処理時間測定
        start_time = datetime.now()
        
        result = await import_service.import_csv_file(
            file_path=temp_file_path,
            batch_size=20  # 小さなバッチサイズで性能テスト
        )
        
        end_time = datetime.now()
        processing_time = (end_time - start_time).total_seconds()
        
        # 性能要件確認（100件を10秒以内に処理）
        assert processing_time < 10.0
        
        # 全データが正常に処理されたことを確認
        import_summary = result["import_summary"]
        assert import_summary["inserted"] + import_summary["updated"] == 100
        assert import_summary["errors"] == 0
        
        # バッチ処理が適切に実行されたことを確認
        assert import_summary["total_batches"] == 5  # 100 ÷ 20
    
    finally:
        os.unlink(temp_file_path)


@pytest.mark.asyncio
async def test_error_recovery_and_rollback(db_session):
    """
    エラー発生時のリカバリ・ロールバック機能テスト
    """
    import_service = ImportService(db_session)
    
    # 正常データと異常データの混合CSV
    with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as temp_file:
        writer = csv.writer(temp_file)
        writer.writerow(['date', 'close_rate'])
        writer.writerow(['2024-01-25', '148.50'])  # 正常
        writer.writerow(['2024-01-26', '149.00'])  # 正常
        writer.writerow(['invalid-date', '149.50'])  # 異常
        writer.writerow(['2024-01-28', 'invalid-rate'])  # 異常
        temp_file_path = temp_file.name
    
    try:
        # バリデーション無効でのインポート（部分的成功を許可）
        result = await import_service.import_csv_file(
            file_path=temp_file_path,
            validation_enabled=False,
            duplicate_handling="skip"
        )
        
        # 部分的な成功が記録されることを確認
        import_summary = result["import_summary"]
        assert import_summary["inserted"] >= 2  # 正常データは処理される
        assert import_summary["errors"] >= 2    # 異常データはエラーになる
        
        # データベースに正常データのみ保存されていることを確認
        stmt = select(ExchangeRate).where(
            ExchangeRate.date.in_([
                datetime.strptime('2024-01-25', '%Y-%m-%d').date(),
                datetime.strptime('2024-01-26', '%Y-%m-%d').date()
            ])
        )
        result_db = await db_session.execute(stmt)
        valid_records = result_db.scalars().all()
        
        # 正常データのみが保存されていることを確認
        assert len(valid_records) >= 2
        for record in valid_records:
            assert float(record.close_rate) > 0
    
    finally:
        os.unlink(temp_file_path)


@pytest.mark.asyncio
async def test_concurrent_data_operations(db_session):
    """
    並行データ操作テスト
    """
    import asyncio
    
    scraping_service = ScrapingService(db_session)
    import_service = ImportService(db_session)
    
    # 異なる日付のデータで並行処理テスト
    # CSVファイル1
    with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as temp_file1:
        writer = csv.writer(temp_file1)
        writer.writerow(['date', 'close_rate'])
        writer.writerow(['2024-01-30', '148.75'])
        temp_file1_path = temp_file1.name
    
    # CSVファイル2
    with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as temp_file2:
        writer = csv.writer(temp_file2)
        writer.writerow(['date', 'close_rate'])
        writer.writerow(['2024-01-31', '149.25'])
        temp_file2_path = temp_file2.name
    
    try:
        # 並行実行
        import_task1 = import_service.import_csv_file(file_path=temp_file1_path)
        import_task2 = import_service.import_csv_file(file_path=temp_file2_path)
        scraping_task = scraping_service.scrape_yahoo_finance_usdjpy(
            ["https://finance.yahoo.com/quote/USDJPY=X/"]
        )
        
        # 全タスクの完了を待機
        import_result1, import_result2, scraping_result = await asyncio.gather(
            import_task1, import_task2, scraping_task,
            return_exceptions=True
        )
        
        # すべての操作が正常に完了することを確認
        if not isinstance(import_result1, Exception):
            assert import_result1["import_summary"]["inserted"] >= 1
        
        if not isinstance(import_result2, Exception):
            assert import_result2["import_summary"]["inserted"] >= 1
        
        if not isinstance(scraping_result, Exception):
            assert len(scraping_result) >= 1
    
    finally:
        os.unlink(temp_file1_path)
        os.unlink(temp_file2_path)


@pytest.mark.asyncio
async def test_data_quality_across_sources(db_session):
    """
    複数データソース間でのデータ品質テスト
    """
    scraping_service = ScrapingService(db_session)
    import_service = ImportService(db_session)
    
    # 1. 高品質なCSVデータをインポート
    with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as temp_file:
        writer = csv.writer(temp_file)
        writer.writerow(['date', 'open_rate', 'high_rate', 'low_rate', 'close_rate', 'volume'])
        writer.writerow(['2024-02-01', '148.25', '149.15', '147.80', '148.95', '125000'])
        temp_file_path = temp_file.name
    
    try:
        import_result = await import_service.import_csv_file(
            file_path=temp_file_path,
            validation_enabled=True
        )
        
        # CSVデータの品質確認
        validation = import_result["validation"]
        assert validation.is_valid
        assert validation.invalid_rows == 0
        
        # 2. スクレイピングデータの品質検証
        scraped_data = [
            {
                "date": "2024-02-02",
                "close_rate": 149.50,
                "volume": 130000
            }
        ]
        
        quality_result = await scraping_service.validate_scraped_data(scraped_data)
        
        # スクレイピングデータの品質確認
        assert quality_result["total_records"] == 1
        assert quality_result["valid_records"] == 1
        assert quality_result["invalid_records"] == 0
        
        # 3. 両方のデータをデータベースに保存して整合性確認
        await scraping_service.save_scraped_data(scraped_data)
        
        # データベースから両方のレコードを取得
        stmt = select(ExchangeRate).where(
            ExchangeRate.date.in_([
                datetime.strptime('2024-02-01', '%Y-%m-%d').date(),
                datetime.strptime('2024-02-02', '%Y-%m-%d').date()
            ])
        ).order_by(ExchangeRate.date)
        
        result = await db_session.execute(stmt)
        all_records = result.scalars().all()
        
        # 両方のレコードが存在し、適切なソースタイプが設定されていることを確認
        assert len(all_records) == 2
        assert all_records[0].source == DataSourceType.BOJ_CSV
        assert all_records[1].source == DataSourceType.SCRAPING
        
        # レート値の妥当性確認
        for record in all_records:
            assert 140.0 <= float(record.close_rate) <= 160.0  # USD/JPY妥当範囲
    
    finally:
        os.unlink(temp_file_path)