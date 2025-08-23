"""
Backtest API Endpoints
======================

バックテスト機能のFastAPIエンドポイント実装
過去データを使用した予測精度検証とパフォーマンス分析API
"""

from datetime import datetime
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from ..database import get_db
from ..services.backtest_service import BacktestService
from ..schemas.backtest import (
    BacktestConfig,
    BacktestJobResponse,
    BacktestResultsResponse,
    BacktestMetricsResponse,
    BacktestTradesResponse
)
from ..models import BacktestResult


router = APIRouter(
    prefix="/api/backtest",
    tags=["backtest"],
    responses={
        404: {"description": "Backtest not found"},
        422: {"description": "Validation error"},
        500: {"description": "Internal server error"}
    }
)


@router.post("/run", response_model=BacktestJobResponse)
async def run_backtest(
    config: BacktestConfig,
    db: AsyncSession = Depends(get_db)
) -> BacktestJobResponse:
    """
    バックテスト実行
    
    指定された設定でバックテストを非同期実行し、ジョブIDを返します。
    実際の処理はバックグラウンドで実行され、結果は別エンドポイントで取得します。
    """
    service = BacktestService(db)
    return await service.start_backtest(config)


@router.get("/results/{job_id}", response_model=BacktestResultsResponse)
async def get_backtest_results(
    job_id: str,
    db: AsyncSession = Depends(get_db)
) -> BacktestResultsResponse:
    """
    バックテスト結果取得
    
    指定されたジョブIDのバックテスト結果を取得します。
    実行中の場合は現在の状況を、完了した場合は最終結果を返します。
    """
    service = BacktestService(db)
    result = await service.get_results(job_id)
    if not result:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Backtest job {job_id} not found"
        )
    return result


@router.get("/metrics/{job_id}", response_model=BacktestMetricsResponse)
async def get_backtest_metrics(
    job_id: str,
    db: AsyncSession = Depends(get_db)
) -> BacktestMetricsResponse:
    """
    バックテスト評価指標取得
    
    指定されたジョブIDのバックテスト評価指標を詳細に取得します。
    パフォーマンス分析、リスク指標、予測精度を含みます。
    """
    service = BacktestService(db)
    metrics = await service.get_metrics(job_id)
    if not metrics:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Backtest metrics for job {job_id} not found or not completed"
        )
    return metrics


@router.get("/trades/{job_id}", response_model=BacktestTradesResponse)
async def get_backtest_trades(
    job_id: str,
    page: int = Query(default=1, ge=1, description="ページ番号"),
    page_size: int = Query(default=100, ge=10, le=1000, description="ページサイズ"),
    db: AsyncSession = Depends(get_db)
) -> BacktestTradesResponse:
    """
    バックテスト取引履歴取得
    
    指定されたジョブIDのバックテスト取引履歴を取得します。
    ページングに対応し、取引の詳細情報と統計サマリーを含みます。
    """
    if page < 1:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Page must be >= 1"
        )
    
    if page_size < 1 or page_size > 1000:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Page size must be between 1 and 1000"
        )
    
    service = BacktestService(db)
    trades = await service.get_trades(job_id, page, page_size)
    if not trades:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Backtest trades for job {job_id} not found"
        )
    return trades




