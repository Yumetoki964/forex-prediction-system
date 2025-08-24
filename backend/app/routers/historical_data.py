"""
Historical data API endpoints
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Dict, Any, List, Optional
from datetime import date, datetime
import logging

from app.database import get_db
from app.services.historical_data_service import HistoricalDataService
from app.core.dependencies import get_current_user

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/api/historical-data",
    tags=["historical-data"]
)

@router.post("/fetch/{currency_pair}")
async def fetch_historical_data(
    currency_pair: str,
    period: str = Query(default="1y", description="Period: 1d, 5d, 1mo, 3mo, 6mo, 1y, 2y, 5y, 10y, ytd, max"),
    db: AsyncSession = Depends(get_db)
    # current_user: dict = Depends(get_current_user)  # 一時的にコメントアウト
) -> Dict[str, Any]:
    """
    Fetch and save historical data for a specific currency pair
    """
    try:
        service = HistoricalDataService()
        result = await service.fetch_and_save(
            db=db,
            currency_pair=currency_pair,
            period=period
        )
        
        return result
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Error fetching historical data: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to fetch historical data")

@router.post("/fetch-multiple")
async def fetch_multiple_pairs(
    currency_pairs: Optional[List[str]] = Query(default=None, description="List of currency pairs"),
    period: str = Query(default="1y", description="Period for historical data"),
    db: AsyncSession = Depends(get_db)
    # current_user: dict = Depends(get_current_user)  # 一時的にコメントアウト
) -> List[Dict[str, Any]]:
    """
    Fetch historical data for multiple currency pairs
    """
    try:
        service = HistoricalDataService()
        
        # Default to USD/JPY if no pairs specified
        if not currency_pairs:
            currency_pairs = ['USD/JPY']
        
        results = await service.fetch_multiple_pairs(
            db=db,
            currency_pairs=currency_pairs,
            period=period
        )
        
        return results
        
    except Exception as e:
        logger.error(f"Error fetching multiple pairs: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to fetch historical data")

@router.get("/summary")
async def get_data_summary(
    currency_pair: Optional[str] = Query(default=None, description="Specific currency pair"),
    db: AsyncSession = Depends(get_db)
    # current_user: dict = Depends(get_current_user)  # 一時的にコメントアウト
) -> Dict[str, Any]:
    """
    Get summary of available historical data
    """
    try:
        service = HistoricalDataService()
        summary = await service.get_data_summary(db, currency_pair)
        
        return summary
        
    except Exception as e:
        logger.error(f"Error getting data summary: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to get data summary")

@router.get("/supported-pairs")
async def get_supported_pairs() -> Dict[str, Any]:
    """
    Get list of supported currency pairs
    """
    service = HistoricalDataService()
    return {
        "supported_pairs": list(service.SUPPORTED_PAIRS.keys()),
        "count": len(service.SUPPORTED_PAIRS)
    }