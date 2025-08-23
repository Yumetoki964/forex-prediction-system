"""
Tests for Phase S-2b: Data Sources Operation Services - Import Service
CSVインポートサービス単体テスト

Phase S-2b-2: Import Service
- エンドポイント 6.3: /api/sources/csv-import - CSV一括インポート
"""

import pytest
import tempfile
import os
import csv
from datetime import datetime, date
from typing import Dict, Any
from decimal import Decimal

from app.services.import_service import ImportService
from app.models import ExchangeRate, DataSourceType
from app.schemas.sources import CSVValidationResult


@pytest.mark.asyncio
async def test_csv_import_basic_functionality(db_session):
    """
    CSV一括インポート基本機能テスト
    """
    service = ImportService(db_session)
    
    # 一時CSVファイル作成
    with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as temp_file:
        writer = csv.writer(temp_file)
        writer.writerow(['date', 'open_rate', 'high_rate', 'low_rate', 'close_rate', 'volume'])
        writer.writerow(['2024-01-15', '148.25', '149.15', '147.80', '148.95', '125000'])
        writer.writerow(['2024-01-16', '148.95', '149.80', '148.30', '149.45', '132000'])
        writer.writerow(['2024-01-17', '149.45', '150.20', '148.90', '149.85', '145000'])
        temp_file_path = temp_file.name
    
    try:
        # CSVインポート実行
        result = await service.import_csv_file(
            file_path=temp_file_path,
            source_type=DataSourceType.BOJ_CSV,
            date_column="date",
            rate_column="close_rate",
            skip_header=True,
            duplicate_handling="skip"
        )
        
        # 結果検証
        assert "file_info" in result
        assert "validation" in result
        assert "import_summary" in result
        assert "preview_data" in result
        
        # ファイル情報確認
        file_info = result["file_info"]
        assert file_info["filename"] == os.path.basename(temp_file_path)
        assert "size" in file_info
        assert "encoding" in file_info
        
        # インポート結果確認
        import_summary = result["import_summary"]
        assert import_summary["inserted"] >= 0
        assert import_summary["errors"] == 0
        
        # プレビューデータ確認
        preview_data = result["preview_data"]
        assert len(preview_data) <= 10
        for item in preview_data:
            assert "date" in item
            assert "close_rate" in item
    
    finally:
        # 一時ファイル削除
        os.unlink(temp_file_path)


@pytest.mark.asyncio
async def test_csv_file_encoding_detection(db_session):
    """
    CSVファイルエンコーディング自動検出テスト
    """
    service = ImportService(db_session)
    
    # UTF-8エンコーディングのテストファイル作成
    with tempfile.NamedTemporaryFile(mode='w', encoding='utf-8', suffix='.csv', delete=False) as temp_file:
        writer = csv.writer(temp_file)
        writer.writerow(['date', 'close_rate'])
        writer.writerow(['2024-01-15', '148.95'])
        temp_file_path = temp_file.name
    
    try:
        # エンコーディング検出テスト
        encoding = await service._detect_encoding(temp_file_path)
        assert encoding in ['UTF-8', 'utf-8']
        
        # 区切り文字検出テスト
        delimiter = await service._detect_delimiter(temp_file_path, encoding)
        assert delimiter == ','
        
    finally:
        os.unlink(temp_file_path)


@pytest.mark.asyncio
async def test_csv_data_validation(db_session):
    """
    CSVデータ検証機能テスト
    """
    service = ImportService(db_session)
    
    # 正常データと異常データの混合CSV作成
    with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as temp_file:
        writer = csv.writer(temp_file)
        writer.writerow(['date', 'close_rate'])
        writer.writerow(['2024-01-15', '148.95'])       # 正常
        writer.writerow(['invalid-date', '149.45'])     # 無効日付
        writer.writerow(['2024-01-17', ''])            # 欠損値
        writer.writerow(['2024-01-18', '-1.0'])        # 無効レート
        writer.writerow(['2024-01-15', '150.00'])      # 重複日付
        temp_file_path = temp_file.name
    
    try:
        # データ検証有効でインポート
        result = await service.import_csv_file(
            file_path=temp_file_path,
            validation_enabled=True,
            duplicate_handling="skip"
        )
        
        validation = result["validation"]
        assert isinstance(validation, CSVValidationResult)
        
        # 検証結果確認
        assert validation.total_rows > 0
        assert validation.valid_rows >= 1
        assert validation.invalid_rows >= 1
        assert validation.duplicate_rows >= 1
        assert len(validation.validation_errors) > 0
        
    finally:
        os.unlink(temp_file_path)


@pytest.mark.asyncio
async def test_duplicate_handling_modes(db_session):
    """
    重複データ処理モードテスト
    """
    service = ImportService(db_session)
    
    # 重複データを含むCSV作成
    with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as temp_file:
        writer = csv.writer(temp_file)
        writer.writerow(['date', 'close_rate'])
        writer.writerow(['2024-01-20', '148.50'])
        temp_file_path = temp_file.name
    
    try:
        # 1回目のインポート（新規データ）
        result1 = await service.import_csv_file(
            file_path=temp_file_path,
            duplicate_handling="skip"
        )
        
        import_summary1 = result1["import_summary"]
        assert import_summary1["inserted"] == 1
        assert import_summary1["skipped"] == 0
        
        # 2回目のインポート（重複データをスキップ）
        result2 = await service.import_csv_file(
            file_path=temp_file_path,
            duplicate_handling="skip"
        )
        
        import_summary2 = result2["import_summary"]
        assert import_summary2["inserted"] == 0
        assert import_summary2["skipped"] == 1
        
        # 3回目のインポート（重複データを更新）
        result3 = await service.import_csv_file(
            file_path=temp_file_path,
            duplicate_handling="update"
        )
        
        import_summary3 = result3["import_summary"]
        assert import_summary3["updated"] == 1
        assert import_summary3["inserted"] == 0
    
    finally:
        os.unlink(temp_file_path)


@pytest.mark.asyncio
async def test_different_date_formats(db_session):
    """
    異なる日付フォーマット対応テスト
    """
    service = ImportService(db_session)
    
    # 異なる日付フォーマットのテストケース
    test_cases = [
        ('%Y-%m-%d', '2024-01-15'),
        ('%Y/%m/%d', '2024/01/15'),
        ('%d/%m/%Y', '15/01/2024'),
    ]
    
    for date_format, date_value in test_cases:
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as temp_file:
            writer = csv.writer(temp_file)
            writer.writerow(['date', 'close_rate'])
            writer.writerow([date_value, '148.95'])
            temp_file_path = temp_file.name
        
        try:
            # 指定された日付フォーマットでインポート
            result = await service.import_csv_file(
                file_path=temp_file_path,
                date_format=date_format
            )
            
            # 正常にインポートされることを確認
            import_summary = result["import_summary"]
            assert import_summary["inserted"] >= 0
            assert import_summary["errors"] == 0
            
        finally:
            os.unlink(temp_file_path)


@pytest.mark.asyncio
async def test_batch_processing(db_session):
    """
    バッチ処理機能テスト
    """
    service = ImportService(db_session)
    
    # 大量データCSV作成（50件）
    with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as temp_file:
        writer = csv.writer(temp_file)
        writer.writerow(['date', 'close_rate'])
        
        base_date = date(2024, 1, 1)
        for i in range(50):
            # 簡単な日付計算（月をまたがないように調整）
            if i < 28:
                current_date = base_date.replace(day=i+1)
            else:
                current_date = base_date.replace(month=2, day=i-27)
            rate = 148.0 + (i * 0.1)
            writer.writerow([current_date.strftime('%Y-%m-%d'), f'{rate:.2f}'])
        
        temp_file_path = temp_file.name
    
    try:
        # 小さなバッチサイズでインポート
        result = await service.import_csv_file(
            file_path=temp_file_path,
            batch_size=10
        )
        
        import_summary = result["import_summary"]
        assert import_summary["batch_size"] == 10
        assert import_summary["total_batches"] == 5  # 50件 ÷ 10件/バッチ
        assert import_summary["inserted"] + import_summary["errors"] <= 50
    
    finally:
        os.unlink(temp_file_path)


@pytest.mark.asyncio
async def test_column_mapping(db_session):
    """
    カラムマッピング機能テスト
    """
    service = ImportService(db_session)
    
    # 異なるカラム名のCSV作成
    with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as temp_file:
        writer = csv.writer(temp_file)
        writer.writerow(['trade_date', 'opening', 'highest', 'lowest', 'closing', 'vol'])
        writer.writerow(['2024-01-21', '148.25', '149.15', '147.80', '148.95', '125000'])
        temp_file_path = temp_file.name
    
    try:
        # カスタムカラムマッピングでインポート
        result = await service.import_csv_file(
            file_path=temp_file_path,
            date_column="trade_date",
            rate_column="closing"
        )
        
        # 正常にインポートされることを確認
        import_summary = result["import_summary"]
        assert import_summary["inserted"] >= 0
        assert import_summary["errors"] == 0
        
        # プレビューデータでマッピング確認
        preview_data = result["preview_data"]
        assert len(preview_data) > 0
        assert preview_data[0]["close_rate"] == 148.95
    
    finally:
        os.unlink(temp_file_path)


@pytest.mark.asyncio
async def test_file_not_found_error(db_session):
    """
    ファイル未発見エラーハンドリングテスト
    """
    service = ImportService(db_session)
    
    # 存在しないファイルパス
    nonexistent_path = "/tmp/nonexistent_file_12345.csv"
    
    # FileNotFoundErrorが発生することを確認
    with pytest.raises(FileNotFoundError):
        await service.import_csv_file(file_path=nonexistent_path)


@pytest.mark.asyncio
async def test_empty_csv_file(db_session):
    """
    空CSVファイル処理テスト
    """
    service = ImportService(db_session)
    
    # 空のCSVファイル作成
    with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as temp_file:
        temp_file.write("")  # 空ファイル
        temp_file_path = temp_file.name
    
    try:
        # 空ファイルのインポート
        result = await service.import_csv_file(file_path=temp_file_path)
        
        # エラーにならず、0件のインポート結果が返される
        import_summary = result["import_summary"]
        assert import_summary["inserted"] == 0
        assert import_summary["updated"] == 0
        assert import_summary["skipped"] == 0
    
    finally:
        os.unlink(temp_file_path)


@pytest.mark.asyncio
async def test_ohlc_data_consistency_validation(db_session):
    """
    OHLC データ整合性検証テスト
    """
    service = ImportService(db_session)
    
    # OHLC整合性違反データを含むCSV作成
    with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as temp_file:
        writer = csv.writer(temp_file)
        writer.writerow(['date', 'open', 'high', 'low', 'close'])
        writer.writerow(['2024-01-15', '148.50', '149.00', '147.50', '148.75'])  # 正常
        writer.writerow(['2024-01-16', '149.00', '148.50', '149.50', '149.25'])  # High < Open
        temp_file_path = temp_file.name
    
    try:
        result = await service.import_csv_file(
            file_path=temp_file_path,
            validation_enabled=True
        )
        
        validation = result["validation"]
        
        # 整合性違反が検出されること
        assert validation.total_rows == 2
        assert validation.invalid_rows >= 1
        assert any("inconsistency" in error.lower() for error in validation.validation_errors)
    
    finally:
        os.unlink(temp_file_path)