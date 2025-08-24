"""
リアルタイム為替レート取得エンドポイント
"""

from fastapi import APIRouter, HTTPException, Depends
from typing import Dict, List
from datetime import datetime

from ..services.forex_scraper import ForexScraper
from ..dependencies import get_current_user

router = APIRouter(prefix="/api/forex", tags=["forex"])

@router.get("/live")
async def get_live_rate(current_user = Depends(get_current_user)) -> Dict:
    """
    現在の為替レートをWebサイトから取得
    
    Returns:
        Dict: 為替レート情報（source, rate, timestamp, currency_pair）
    """
    try:
        scraper = ForexScraper()
        rate_data = await scraper.get_current_rate()
        return {
            "success": True,
            "data": rate_data,
            "message": f"Rate fetched from {rate_data['source']}"
        }
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to fetch forex rate: {str(e)}"
        )

@router.get("/live/all")
async def get_all_rates(current_user = Depends(get_current_user)) -> Dict:
    """
    複数のソースから為替レートを取得
    
    Returns:
        Dict: 複数ソースの為替レート情報
    """
    try:
        scraper = ForexScraper()
        rates = await scraper.get_multiple_rates()
        
        # 平均レートを計算
        if rates:
            avg_rate = sum(r['rate'] for r in rates) / len(rates)
        else:
            avg_rate = 0
        
        return {
            "success": True,
            "data": {
                "rates": rates,
                "average_rate": round(avg_rate, 2),
                "count": len(rates),
                "timestamp": datetime.now().isoformat()
            },
            "message": f"Fetched rates from {len(rates)} sources"
        }
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to fetch forex rates: {str(e)}"
        )

@router.post("/collect/web")
async def collect_from_web(current_user = Depends(get_current_user)) -> Dict:
    """
    Webサイトから為替データを収集して保存（シミュレーション）
    
    Returns:
        Dict: 収集結果
    """
    try:
        scraper = ForexScraper()
        rate_data = await scraper.get_current_rate()
        
        # ここで実際にはデータベースに保存する処理を行う
        # 現在はシミュレーション
        
        return {
            "success": True,
            "data": {
                "collected_rate": rate_data,
                "saved": True,
                "message": "Rate collected and saved successfully (demo mode)"
            }
        }
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to collect forex data: {str(e)}"
        )