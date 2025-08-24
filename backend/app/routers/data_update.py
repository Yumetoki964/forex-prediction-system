"""
データ更新管理APIエンドポイント
"""
from fastapi import APIRouter, HTTPException, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Dict, Any, List, Optional
from datetime import date
import logging

from app.database import get_db
from app.services.data_update_service import DataUpdateService
from app.core.dependencies import get_current_user

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/api/data-update",
    tags=["data-update"]
)

@router.get("/gaps")
async def detect_data_gaps(
    currency_pair: str = Query(default="USD/JPY", description="Currency pair"),
    start_date: Optional[date] = Query(default=None, description="Start date"),
    end_date: Optional[date] = Query(default=None, description="End date"),
    db: AsyncSession = Depends(get_db)
    # current_user: dict = Depends(get_current_user)
) -> List[Dict[str, Any]]:
    """
    データの欠損期間を検出
    """
    try:
        service = DataUpdateService()
        gaps = await service.get_data_gaps(
            db=db,
            currency_pair=currency_pair,
            start_date=start_date,
            end_date=end_date
        )
        
        return gaps
        
    except Exception as e:
        logger.error(f"Error detecting data gaps: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to detect data gaps")

@router.post("/gaps/fill")
async def fill_data_gaps(
    currency_pair: str = Query(default="USD/JPY", description="Currency pair"),
    max_days: int = Query(default=30, description="Maximum days to fetch at once"),
    db: AsyncSession = Depends(get_db)
    # current_user: dict = Depends(get_current_user)
) -> Dict[str, Any]:
    """
    データの欠損を自動的に埋める
    """
    try:
        service = DataUpdateService()
        result = await service.fill_data_gaps(
            db=db,
            currency_pair=currency_pair,
            max_days=max_days
        )
        
        return result
        
    except Exception as e:
        logger.error(f"Error filling data gaps: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to fill data gaps")

@router.post("/latest")
async def update_latest_data(
    currency_pairs: Optional[List[str]] = Query(default=None, description="Currency pairs to update"),
    db: AsyncSession = Depends(get_db)
    # current_user: dict = Depends(get_current_user)
) -> Dict[str, Any]:
    """
    最新データを更新（過去3日分）
    """
    try:
        service = DataUpdateService()
        result = await service.update_latest_data(
            db=db,
            currency_pairs=currency_pairs
        )
        
        return result
        
    except Exception as e:
        logger.error(f"Error updating latest data: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to update latest data")

@router.get("/statistics")
async def get_update_statistics(
    days: int = Query(default=30, description="Number of days for statistics"),
    db: AsyncSession = Depends(get_db)
    # current_user: dict = Depends(get_current_user)
) -> Dict[str, Any]:
    """
    データ更新統計を取得
    """
    try:
        service = DataUpdateService()
        stats = await service.get_update_statistics(
            db=db,
            days=days
        )
        
        return stats
        
    except Exception as e:
        logger.error(f"Error getting update statistics: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to get update statistics")

@router.get("/integrity")
async def validate_data_integrity(
    currency_pair: str = Query(default="USD/JPY", description="Currency pair"),
    days: int = Query(default=30, description="Number of days to validate"),
    db: AsyncSession = Depends(get_db)
    # current_user: dict = Depends(get_current_user)
) -> Dict[str, Any]:
    """
    データの整合性を検証
    """
    try:
        service = DataUpdateService()
        result = await service.validate_data_integrity(
            db=db,
            currency_pair=currency_pair,
            days=days
        )
        
        return result
        
    except Exception as e:
        logger.error(f"Error validating data integrity: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to validate data integrity")