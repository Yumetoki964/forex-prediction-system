"""
Backtest API Endpoints
=====================

バックテスト機能のFastAPIエンドポイント実装
過去データを使用した予測精度検証とパフォーマンス分析API
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.schemas.backtest import (
    BacktestConfig,
    BacktestJobResponse,
    BacktestResultsResponse,
    BacktestMetricsResponse,
    BacktestTradesResponse,
)
from app.services.backtest_service import BacktestService

router = APIRouter()


@router.post("/run", response_model=BacktestJobResponse)
async def run_backtest(
    config: BacktestConfig,
    db: AsyncSession = Depends(get_db)
) -> BacktestJobResponse:
    """
    バックテスト実行
    
    過去データを使用して予測モデルの性能を検証するバックテストを開始する。
    非同期処理で実行され、job_idを返却する。
    
    Args:
        config: バックテスト設定
        db: データベースセッション
    
    Returns:
        BacktestJobResponse: ジョブ情報
    
    Raises:
        HTTPException: 設定エラーまたは実行失敗時
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
    
    指定されたジョブIDのバックテスト結果を取得する。
    実行中の場合は進捗状況を返す。
    
    Args:
        job_id: バックテストジョブID
        db: データベースセッション
    
    Returns:
        BacktestResultsResponse: バックテスト結果
    
    Raises:
        HTTPException: ジョブが見つからない場合
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
    
    指定されたジョブIDの詳細な評価指標を取得する。
    シャープレシオ、最大ドローダウン、予測精度等を含む。
    
    Args:
        job_id: バックテストジョブID
        db: データベースセッション
    
    Returns:
        BacktestMetricsResponse: 詳細評価指標
    
    Raises:
        HTTPException: ジョブが見つからないか完了していない場合
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
    page: int = 1,
    page_size: int = 100,
    db: AsyncSession = Depends(get_db)
) -> BacktestTradesResponse:
    """
    バックテスト取引履歴取得
    
    指定されたジョブIDのバックテスト取引履歴を取得する。
    ページネーション対応で大量の取引データを効率的に取得可能。
    
    Args:
        job_id: バックテストジョブID
        page: ページ番号（1から開始）
        page_size: 1ページあたりの取引数（最大1000）
        db: データベースセッション
    
    Returns:
        BacktestTradesResponse: 取引履歴データ
    
    Raises:
        HTTPException: ジョブが見つからない場合やページパラメータが不正な場合
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