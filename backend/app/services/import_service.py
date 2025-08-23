"""
Import Service for Forex Prediction System

CSVファイルからの為替データ一括インポート機能を提供するサービス層実装
- 日銀CSVファイルの処理
- データ検証とバリデーション
- 重複データ処理（スキップ/更新/エラー）
- バッチ処理による高速インポート
"""

import os
import csv
import asyncio
from typing import List, Dict, Optional, Any, IO
from datetime import datetime, date
import logging
from decimal import Decimal, InvalidOperation
import chardet
from pathlib import Path

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_

from ..models import ExchangeRate, DataSource, DataSourceType
from ..schemas.sources import CSVValidationResult

logger = logging.getLogger(__name__)


class ImportService:
    """CSV一括インポートサービス"""
    
    def __init__(self, db: AsyncSession):
        self.db = db
        
    async def import_csv_file(
        self,
        file_path: str,
        source_type: DataSourceType = DataSourceType.BOJ_CSV,
        date_column: str = "date",
        rate_column: str = "close_rate",
        skip_header: bool = True,
        date_format: str = "%Y-%m-%d",
        validation_enabled: bool = True,
        duplicate_handling: str = "skip",
        batch_size: int = 100
    ) -> Dict[str, Any]:
        """
        CSVファイルからデータを一括インポート
        
        Args:
            file_path: CSVファイルパス
            source_type: データソース種別
            date_column: 日付カラム名
            rate_column: レートカラム名
            skip_header: ヘッダー行スキップ
            date_format: 日付フォーマット
            validation_enabled: データ検証有効化
            duplicate_handling: 重複処理方式（skip/update/error）
            batch_size: バッチサイズ
            
        Returns:
            Dict[str, Any]: インポート結果
        """
        try:
            # ファイル存在確認
            if not os.path.exists(file_path):
                raise FileNotFoundError(f"CSV file not found: {file_path}")
            
            # ファイル情報取得
            file_info = await self._get_file_info(file_path)
            
            # CSVデータ読み込み
            csv_data = await self._read_csv_file(
                file_path, skip_header, date_column, rate_column, date_format
            )
            
            # データ検証
            validation_result = None
            if validation_enabled:
                validation_result = await self._validate_csv_data(csv_data, date_format)
                if not validation_result.is_valid and duplicate_handling == "error":
                    raise ValueError(f"CSV validation failed: {len(validation_result.validation_errors)} errors")
            
            # データインポート実行
            import_summary = await self._execute_import(
                csv_data, source_type, duplicate_handling, batch_size
            )
            
            # プレビューデータ作成
            preview_data = await self._create_preview_data(csv_data[:10])
            
            return {
                "file_info": file_info,
                "validation": validation_result,
                "import_summary": import_summary,
                "preview_data": preview_data
            }
            
        except Exception as e:
            logger.error(f"CSV import failed for {file_path}: {str(e)}")
            await self.db.rollback()
            raise
    
    async def _get_file_info(self, file_path: str) -> Dict[str, str]:
        """
        ファイル情報を取得
        """
        try:
            stat = os.stat(file_path)
            
            # ファイルサイズ（MB）
            size_mb = round(stat.st_size / (1024 * 1024), 2)
            size_str = f"{size_mb}MB" if size_mb >= 1 else f"{stat.st_size}B"
            
            # エンコーディング検出
            encoding = await self._detect_encoding(file_path)
            
            # 区切り文字検出
            delimiter = await self._detect_delimiter(file_path, encoding)
            
            return {
                "filename": os.path.basename(file_path),
                "size": size_str,
                "encoding": encoding,
                "delimiter": delimiter,
                "last_modified": datetime.fromtimestamp(stat.st_mtime).strftime("%Y-%m-%dT%H:%M:%S")
            }
            
        except Exception as e:
            logger.error(f"Error getting file info: {str(e)}")
            return {
                "filename": os.path.basename(file_path),
                "size": "Unknown",
                "encoding": "UTF-8",
                "delimiter": ",",
                "last_modified": datetime.now().strftime("%Y-%m-%dT%H:%M:%S")
            }
    
    async def _detect_encoding(self, file_path: str) -> str:
        """
        ファイルエンコーディングを検出
        """
        try:
            with open(file_path, 'rb') as file:
                raw_data = file.read(8192)  # 最初の8KB読み込み
                result = chardet.detect(raw_data)
                return result['encoding'] if result['encoding'] else 'UTF-8'
        except Exception:
            return 'UTF-8'
    
    async def _detect_delimiter(self, file_path: str, encoding: str) -> str:
        """
        CSV区切り文字を検出
        """
        try:
            with open(file_path, 'r', encoding=encoding) as file:
                sample = file.read(1024)
                sniffer = csv.Sniffer()
                delimiter = sniffer.sniff(sample).delimiter
                return delimiter
        except Exception:
            return ','
    
    async def _read_csv_file(
        self,
        file_path: str,
        skip_header: bool,
        date_column: str,
        rate_column: str,
        date_format: str
    ) -> List[Dict[str, Any]]:
        """
        CSVファイルを読み込み、標準形式に変換
        """
        csv_data = []
        encoding = await self._detect_encoding(file_path)
        delimiter = await self._detect_delimiter(file_path, encoding)
        
        try:
            with open(file_path, 'r', encoding=encoding) as file:
                reader = csv.DictReader(file, delimiter=delimiter)
                
                # ヘッダースキップ
                if skip_header and reader.fieldnames:
                    next(reader, None)
                
                for row_idx, row in enumerate(reader):
                    try:
                        # 日付カラム確認
                        if date_column not in row:
                            logger.warning(f"Date column '{date_column}' not found in row {row_idx}")
                            continue
                        
                        # レートカラム確認
                        if rate_column not in row:
                            logger.warning(f"Rate column '{rate_column}' not found in row {row_idx}")
                            continue
                        
                        # データ変換
                        converted_row = await self._convert_csv_row(
                            row, date_column, rate_column, date_format, row_idx
                        )
                        
                        if converted_row:
                            csv_data.append(converted_row)
                            
                    except Exception as e:
                        logger.warning(f"Error processing row {row_idx}: {str(e)}")
                        continue
            
            logger.info(f"Successfully read {len(csv_data)} records from CSV")
            return csv_data
            
        except Exception as e:
            logger.error(f"Error reading CSV file: {str(e)}")
            raise
    
    async def _convert_csv_row(
        self,
        row: Dict[str, str],
        date_column: str,
        rate_column: str,
        date_format: str,
        row_idx: int
    ) -> Optional[Dict[str, Any]]:
        """
        CSV行を標準フォーマットに変換
        """
        try:
            # 日付変換
            date_str = row[date_column].strip()
            if not date_str:
                return None
            
            parsed_date = datetime.strptime(date_str, date_format).date()
            
            # レート変換
            rate_str = row[rate_column].strip().replace(',', '')
            if not rate_str:
                return None
            
            close_rate = float(rate_str)
            
            # オプションフィールド
            open_rate = self._safe_float_conversion(row.get('open_rate', row.get('open', '')))
            high_rate = self._safe_float_conversion(row.get('high_rate', row.get('high', '')))
            low_rate = self._safe_float_conversion(row.get('low_rate', row.get('low', '')))
            volume = self._safe_int_conversion(row.get('volume', ''))
            
            return {
                "date": parsed_date.strftime('%Y-%m-%d'),
                "open_rate": open_rate,
                "high_rate": high_rate,
                "low_rate": low_rate,
                "close_rate": close_rate,
                "volume": volume,
                "row_index": row_idx
            }
            
        except Exception as e:
            logger.warning(f"Error converting CSV row {row_idx}: {str(e)}")
            return None
    
    def _safe_float_conversion(self, value: str) -> Optional[float]:
        """
        文字列を安全にfloatに変換
        """
        if not value or not value.strip():
            return None
        try:
            return float(value.strip().replace(',', ''))
        except ValueError:
            return None
    
    def _safe_int_conversion(self, value: str) -> Optional[int]:
        """
        文字列を安全にintに変換
        """
        if not value or not value.strip():
            return None
        try:
            return int(float(value.strip().replace(',', '')))
        except ValueError:
            return None
    
    async def _validate_csv_data(
        self,
        csv_data: List[Dict[str, Any]],
        date_format: str
    ) -> CSVValidationResult:
        """
        CSVデータを検証
        """
        validation_errors = []
        valid_rows = 0
        invalid_rows = 0
        duplicate_rows = 0
        missing_values = 0
        dates = []
        
        seen_dates = set()
        
        for i, row in enumerate(csv_data):
            is_valid = True
            row_errors = []
            
            # 必須フィールドチェック
            if not row.get('date'):
                row_errors.append("Missing date")
                missing_values += 1
                is_valid = False
            
            if not row.get('close_rate'):
                row_errors.append("Missing close rate")
                missing_values += 1
                is_valid = False
            
            # 日付重複チェック
            if row.get('date'):
                if row['date'] in seen_dates:
                    duplicate_rows += 1
                    row_errors.append("Duplicate date")
                else:
                    seen_dates.add(row['date'])
                    try:
                        dates.append(datetime.strptime(row['date'], '%Y-%m-%d'))
                    except ValueError:
                        row_errors.append("Invalid date format")
                        is_valid = False
            
            # レート値検証
            if row.get('close_rate'):
                try:
                    rate = float(row['close_rate'])
                    if rate <= 0 or rate > 1000:
                        row_errors.append(f"Invalid rate value: {rate}")
                        is_valid = False
                except (ValueError, TypeError):
                    row_errors.append("Invalid rate format")
                    is_valid = False
            
            # OHLC整合性チェック
            if all(row.get(field) for field in ['open_rate', 'high_rate', 'low_rate', 'close_rate']):
                try:
                    o, h, l, c = [float(row[field]) for field in ['open_rate', 'high_rate', 'low_rate', 'close_rate']]
                    if h < max(o, l, c) or l > min(o, h, c):
                        row_errors.append("OHLC data inconsistency")
                        is_valid = False
                except ValueError:
                    pass  # 既に他のチェックで捕捉済み
            
            if is_valid:
                valid_rows += 1
            else:
                invalid_rows += 1
                validation_errors.extend([
                    f"Row {row.get('row_index', i)+1}: {error}" 
                    for error in row_errors
                ])
        
        # 日付範囲
        date_range_start = min(dates) if dates else None
        date_range_end = max(dates) if dates else None
        
        return CSVValidationResult(
            is_valid=(invalid_rows == 0),
            total_rows=len(csv_data),
            valid_rows=valid_rows,
            invalid_rows=invalid_rows,
            duplicate_rows=duplicate_rows,
            missing_values=missing_values,
            date_range_start=date_range_start,
            date_range_end=date_range_end,
            validation_errors=validation_errors
        )
    
    async def _execute_import(
        self,
        csv_data: List[Dict[str, Any]],
        source_type: DataSourceType,
        duplicate_handling: str,
        batch_size: int
    ) -> Dict[str, int]:
        """
        データベースへの実際のインポート実行
        """
        import_summary = {
            "inserted": 0,
            "updated": 0,
            "skipped": 0,
            "errors": 0,
            "batch_size": batch_size,
            "total_batches": (len(csv_data) + batch_size - 1) // batch_size
        }
        
        try:
            # バッチ処理でインポート
            for i in range(0, len(csv_data), batch_size):
                batch = csv_data[i:i + batch_size]
                
                for row in batch:
                    try:
                        result = await self._import_single_record(
                            row, source_type, duplicate_handling
                        )
                        import_summary[result] += 1
                        
                    except Exception as e:
                        logger.error(f"Error importing record {row.get('date')}: {str(e)}")
                        import_summary["errors"] += 1
                
                # バッチ毎にコミット
                await self.db.commit()
                logger.info(f"Imported batch {(i // batch_size) + 1}/{import_summary['total_batches']}")
            
            return import_summary
            
        except Exception as e:
            await self.db.rollback()
            logger.error(f"Import execution failed: {str(e)}")
            raise
    
    async def _import_single_record(
        self,
        row: Dict[str, Any],
        source_type: DataSourceType,
        duplicate_handling: str
    ) -> str:
        """
        単一レコードのインポート処理
        
        Returns:
            str: 処理結果 ("inserted", "updated", "skipped")
        """
        try:
            # 日付変換
            record_date = datetime.strptime(row['date'], '%Y-%m-%d').date()
            
            # 既存レコード確認
            stmt = select(ExchangeRate).where(ExchangeRate.date == record_date)
            result = await self.db.execute(stmt)
            existing_record = result.scalar_one_or_none()
            
            if existing_record:
                # 重複処理
                if duplicate_handling == "skip":
                    return "skipped"
                elif duplicate_handling == "update":
                    # 更新
                    if row.get('open_rate'):
                        existing_record.open_rate = Decimal(str(row['open_rate']))
                    if row.get('high_rate'):
                        existing_record.high_rate = Decimal(str(row['high_rate']))
                    if row.get('low_rate'):
                        existing_record.low_rate = Decimal(str(row['low_rate']))
                    if row.get('close_rate'):
                        existing_record.close_rate = Decimal(str(row['close_rate']))
                    if row.get('volume'):
                        existing_record.volume = row['volume']
                    
                    existing_record.source = source_type
                    existing_record.updated_at = datetime.now()
                    return "updated"
                elif duplicate_handling == "error":
                    raise ValueError(f"Duplicate record for date {record_date}")
            else:
                # 新規挿入
                new_record = ExchangeRate(
                    date=record_date,
                    open_rate=Decimal(str(row['open_rate'])) if row.get('open_rate') else None,
                    high_rate=Decimal(str(row['high_rate'])) if row.get('high_rate') else None,
                    low_rate=Decimal(str(row['low_rate'])) if row.get('low_rate') else None,
                    close_rate=Decimal(str(row['close_rate'])),
                    volume=row.get('volume'),
                    source=source_type,
                    is_holiday=False,
                    is_interpolated=False
                )
                
                self.db.add(new_record)
                return "inserted"
                
        except Exception as e:
            logger.error(f"Error importing record {row.get('date')}: {str(e)}")
            raise
    
    async def _create_preview_data(
        self,
        csv_data: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """
        プレビューデータ作成
        """
        preview_data = []
        
        for row in csv_data:
            preview_row = {
                "date": row.get('date'),
                "open_rate": row.get('open_rate'),
                "high_rate": row.get('high_rate'),
                "low_rate": row.get('low_rate'),
                "close_rate": row.get('close_rate'),
                "volume": row.get('volume'),
                "source": "csv_import"
            }
            preview_data.append(preview_row)
        
        return preview_data[:10]  # 最大10件のプレビュー