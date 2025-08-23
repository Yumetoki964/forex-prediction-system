"""
Data Sources API Router

データソース管理API endpoints
- 6.1: /api/sources/status (GET) - データソース稼働状況取得
- 6.2: /api/sources/scrape (POST) - Webスクレイピング実行
- 6.3: /api/sources/csv-import (POST) - CSV一括インポート
- 6.4: /api/sources/health (GET) - ソースヘルスチェック
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from typing import List
import uuid
import os
import logging

from ..database import get_db
from ..schemas.sources import (
    SourcesStatusResponse,
    SourcesHealthResponse,
    DataSourceStatusItem,
    DataSourcesSummary,
    SourceHealthItem,
    HealthCheckSummary,
    DataSourceTypeEnum,
    DataSourceStatusEnum,
    HealthStatusEnum,
    ScrapeRequest,
    ScrapeResponse,
    ScrapeResultItem,
    CSVImportRequest,
    CSVImportResponse,
    CSVValidationResult,
    SourcesErrorResponse
)
from ..models import DataSource
from ..services.sources_service import SourcesService
from ..services.scraping_service import ScrapingService
from ..services.import_service import ImportService

router = APIRouter()
logger = logging.getLogger(__name__)


@router.get("/status", response_model=SourcesStatusResponse, 
           summary="データソース稼働状況取得",
           description="全データソースの稼働状況と統計情報を取得します",
           responses={
               200: {"description": "データソース状況取得成功"},
               500: {"model": SourcesErrorResponse, "description": "サーバーエラー"}
           })
async def get_sources_status(db: Session = Depends(get_db)) -> SourcesStatusResponse:
    """
    データソース稼働状況取得 (6.1)
    
    全データソースの稼働状況と統計情報を取得
    - 各ソースの詳細状態
    - 成功率とレスポンス時間
    - レート制限状況
    - 概要統計
    """
    try:
        service = SourcesService(db)
        return await service.get_sources_status()
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve sources status: {str(e)}"
        )


@router.get("/health", response_model=SourcesHealthResponse,
           summary="ソースヘルスチェック",
           description="全データソースのヘルスチェックを実行し、接続性とデータ取得可能性を確認します",
           responses={
               200: {"description": "ヘルスチェック実行成功"},
               500: {"model": SourcesErrorResponse, "description": "サーバーエラー"}
           })
async def check_sources_health(db: Session = Depends(get_db)) -> SourcesHealthResponse:
    """
    ソースヘルスチェック (6.4)
    
    全データソースのヘルスチェックを実行
    - 接続性の確認
    - データ取得可能性の検証
    - レスポンス時間の測定
    - レート制限状況の確認
    """
    try:
        service = SourcesService(db)
        return await service.check_sources_health()
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to perform health check: {str(e)}"
        )


@router.post("/scrape", response_model=ScrapeResponse,
            summary="Webスクレイピング実行",
            description="指定されたURLからWebスクレイピングを実行して為替データを取得します",
            responses={
                200: {"description": "スクレイピング実行成功"},
                400: {"model": SourcesErrorResponse, "description": "リクエストエラー"},
                500: {"model": SourcesErrorResponse, "description": "サーバーエラー"}
            })
async def scrape_data(
    request: ScrapeRequest,
    db: Session = Depends(get_db)
) -> ScrapeResponse:
    """
    Webスクレイピング実行 (6.2)
    
    指定されたURLからWebスクレイピングを実行
    - 複数URL同時スクレイピング
    - 日付範囲指定による絞り込み
    - データ検証とプレビュー機能
    - レスポンス時間測定
    """
    try:
        # バリデーション
        if not request.target_urls:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="At least one target URL is required"
            )
        
        # ジョブID生成
        job_id = str(uuid.uuid4())
        start_time = datetime.now()
        
        # スクレイピングサービス実行
        scraping_service = ScrapingService(db)
        results = await scraping_service.scrape_yahoo_finance_usdjpy(
            target_urls=request.target_urls,
            date_range_start=request.date_range_start,
            date_range_end=request.date_range_end
        )
        
        # 結果集計
        total_records = 0
        successful_urls = 0
        failed_urls = 0
        
        for result in results:
            if result.success:
                successful_urls += 1
                total_records += result.records_extracted
            else:
                failed_urls += 1
        
        # スクレイピングしたデータをデータベースに保存
        if total_records > 0:
            try:
                # 成功した結果からデータを抽出してDB保存
                all_scraped_data = []
                for result in results:
                    if result.success and result.data_preview:
                        all_scraped_data.extend(result.data_preview)
                
                if all_scraped_data:
                    saved_count = await scraping_service.save_scraped_data(all_scraped_data)
                    logger.info(f"Saved {saved_count} scraped records to database")
            except Exception as save_error:
                logger.error(f"Error saving scraped data: {str(save_error)}")
                # 保存エラーは致命的ではないので、処理を継続
        
        # 完了時刻計算
        completed_at = datetime.now()
        execution_time = int((completed_at - start_time).total_seconds() * 1000)
        
        return ScrapeResponse(
            job_id=job_id,
            status="completed" if failed_urls == 0 else "partially_completed",
            total_urls=len(request.target_urls),
            successful_urls=successful_urls,
            failed_urls=failed_urls,
            total_records=total_records,
            results=results,
            execution_time_ms=execution_time,
            started_at=start_time,
            completed_at=completed_at
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to execute web scraping: {str(e)}"
        )


@router.post("/csv-import", response_model=CSVImportResponse,
            summary="CSV一括インポート",
            description="CSVファイルから為替データを一括インポートします",
            responses={
                200: {"description": "CSVインポート実行成功"},
                400: {"model": SourcesErrorResponse, "description": "リクエストエラー"},
                404: {"model": SourcesErrorResponse, "description": "ファイル未発見"},
                500: {"model": SourcesErrorResponse, "description": "サーバーエラー"}
            })
async def import_csv_data(
    request: CSVImportRequest,
    db: Session = Depends(get_db)
) -> CSVImportResponse:
    """
    CSV一括インポート実行 (6.3)
    
    CSVファイルから為替データを一括インポート
    - ファイル検証とデータ品質チェック
    - 重複データの処理（スキップ/更新/エラー）
    - バッチ処理による高速インポート
    - インポート進捗の追跡
    """
    try:
        # ファイル存在確認
        if not os.path.exists(request.file_path):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"CSV file not found: {request.file_path}"
            )
        
        # ジョブID生成
        job_id = str(uuid.uuid4())
        start_time = datetime.now()
        
        # CSVインポートサービス実行
        import_service = ImportService(db)
        import_result = await import_service.import_csv_file(
            file_path=request.file_path,
            source_type=request.source_type,
            date_column=request.date_column,
            rate_column=request.rate_column,
            skip_header=request.skip_header,
            date_format=request.date_format,
            validation_enabled=request.validation_enabled,
            duplicate_handling=request.duplicate_handling
        )
        
        # 結果から必要な情報を抽出
        file_info = import_result["file_info"]
        validation = import_result["validation"]
        import_summary = import_result["import_summary"]
        preview_data = import_result["preview_data"]
        
        # 完了時刻計算
        completed_at = datetime.now()
        execution_time = int((completed_at - start_time).total_seconds() * 1000)
        
        # ステータス判定
        status_text = "completed"
        if validation and (validation.invalid_rows > 0 or import_summary["errors"] > 0):
            status_text = "completed_with_warnings"
        
        return CSVImportResponse(
            job_id=job_id,
            status=status_text,
            file_info=file_info,
            validation=validation,
            import_summary=import_summary,
            execution_time_ms=execution_time,
            started_at=start_time,
            completed_at=completed_at,
            preview_data=preview_data
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to import CSV data: {str(e)}"
        )