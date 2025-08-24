"""
スケジューラー管理APIエンドポイント
"""
from fastapi import APIRouter, HTTPException, Depends
from typing import Dict, Any, List
import logging

from app.services.scheduler_service import scheduler_service
from app.core.dependencies import get_current_user

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/api/scheduler",
    tags=["scheduler"]
)

@router.get("/status")
async def get_scheduler_status(
    # current_user: dict = Depends(get_current_user)
) -> Dict[str, Any]:
    """
    スケジューラーの現在のステータスを取得
    """
    try:
        return scheduler_service.get_job_status()
    except Exception as e:
        logger.error(f"Error getting scheduler status: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to get scheduler status")

@router.post("/start")
async def start_scheduler(
    # current_user: dict = Depends(get_current_user)
) -> Dict[str, str]:
    """
    スケジューラーを開始
    """
    try:
        await scheduler_service.start()
        return {"message": "Scheduler started successfully"}
    except Exception as e:
        logger.error(f"Error starting scheduler: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to start scheduler")

@router.post("/stop")
async def stop_scheduler(
    # current_user: dict = Depends(get_current_user)
) -> Dict[str, str]:
    """
    スケジューラーを停止
    """
    try:
        scheduler_service.stop()
        return {"message": "Scheduler stopped successfully"}
    except Exception as e:
        logger.error(f"Error stopping scheduler: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to stop scheduler")

@router.post("/jobs/{job_id}/trigger")
async def trigger_job(
    job_id: str,
    # current_user: dict = Depends(get_current_user)
) -> Dict[str, Any]:
    """
    特定のジョブを手動実行
    """
    try:
        result = await scheduler_service.trigger_job(job_id)
        return result
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error(f"Error triggering job {job_id}: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to trigger job")

@router.post("/jobs/{job_id}/pause")
async def pause_job(
    job_id: str,
    # current_user: dict = Depends(get_current_user)
) -> Dict[str, str]:
    """
    特定のジョブを一時停止
    """
    try:
        scheduler_service.pause_job(job_id)
        return {"message": f"Job {job_id} paused successfully"}
    except Exception as e:
        logger.error(f"Error pausing job {job_id}: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to pause job")

@router.post("/jobs/{job_id}/resume")
async def resume_job(
    job_id: str,
    # current_user: dict = Depends(get_current_user)
) -> Dict[str, str]:
    """
    一時停止中のジョブを再開
    """
    try:
        scheduler_service.resume_job(job_id)
        return {"message": f"Job {job_id} resumed successfully"}
    except Exception as e:
        logger.error(f"Error resuming job {job_id}: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to resume job")

@router.post("/collect/daily")
async def trigger_daily_collection(
    # current_user: dict = Depends(get_current_user)
) -> Dict[str, Any]:
    """
    日次データ収集を手動実行
    """
    try:
        await scheduler_service.collect_daily_data()
        return {
            "message": "Daily data collection triggered",
            "status": "completed"
        }
    except Exception as e:
        logger.error(f"Error in manual daily collection: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to collect daily data")

@router.post("/collect/realtime")
async def trigger_realtime_collection(
    # current_user: dict = Depends(get_current_user)
) -> Dict[str, Any]:
    """
    リアルタイムデータ収集を手動実行
    """
    try:
        await scheduler_service.collect_realtime_data()
        return {
            "message": "Realtime data collection triggered",
            "status": "completed"
        }
    except Exception as e:
        logger.error(f"Error in manual realtime collection: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to collect realtime data")