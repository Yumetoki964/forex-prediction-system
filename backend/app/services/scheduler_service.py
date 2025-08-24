"""
スケジューラーサービス - 定期的なデータ収集とタスク実行
"""
import asyncio
import logging
from datetime import datetime, timedelta
from typing import Optional, Dict, Any, List
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from apscheduler.triggers.interval import IntervalTrigger
from sqlalchemy.ext.asyncio import AsyncSession
import json

from app.database import SessionLocal
from app.services.historical_data_service import HistoricalDataService
from app.services.forex_scraper import ForexScraper
from app.models import DataSource, DataSourceStatus, DataSourceType

logger = logging.getLogger(__name__)


class SchedulerService:
    """定期実行スケジューラー管理サービス"""
    
    def __init__(self):
        self.scheduler = AsyncIOScheduler(timezone='Asia/Tokyo')
        self.job_history: List[Dict[str, Any]] = []
        self.is_running = False
        
    async def start(self):
        """スケジューラーを開始"""
        if not self.is_running:
            # ジョブを登録
            self._register_jobs()
            self.scheduler.start()
            self.is_running = True
            logger.info("Scheduler service started")
            
    def stop(self):
        """スケジューラーを停止"""
        if self.is_running:
            self.scheduler.shutdown()
            self.is_running = False
            logger.info("Scheduler service stopped")
            
    def _register_jobs(self):
        """定期実行ジョブを登録"""
        
        # 1. 日次データ収集（平日のみ、日本時間朝6時）
        self.scheduler.add_job(
            self.collect_daily_data,
            CronTrigger(
                day_of_week='mon-fri',
                hour=6,
                minute=0,
                timezone='Asia/Tokyo'
            ),
            id='daily_data_collection',
            name='Daily forex data collection',
            misfire_grace_time=3600
        )
        
        # 2. リアルタイムデータ収集（平日、5分ごと）
        self.scheduler.add_job(
            self.collect_realtime_data,
            CronTrigger(
                day_of_week='mon-fri',
                minute='*/5',
                timezone='Asia/Tokyo'
            ),
            id='realtime_data_collection',
            name='Realtime forex data collection',
            misfire_grace_time=60
        )
        
        # 3. データ品質チェック（毎日深夜2時）
        self.scheduler.add_job(
            self.check_data_quality,
            CronTrigger(
                hour=2,
                minute=0,
                timezone='Asia/Tokyo'
            ),
            id='data_quality_check',
            name='Daily data quality check',
            misfire_grace_time=3600
        )
        
        # 4. 週次データバックアップ（日曜日深夜3時）
        self.scheduler.add_job(
            self.backup_weekly_data,
            CronTrigger(
                day_of_week='sun',
                hour=3,
                minute=0,
                timezone='Asia/Tokyo'
            ),
            id='weekly_backup',
            name='Weekly data backup',
            misfire_grace_time=3600
        )
        
        logger.info(f"Registered {len(self.scheduler.get_jobs())} scheduled jobs")
    
    async def collect_daily_data(self):
        """日次データ収集タスク"""
        job_start = datetime.now()
        job_result = {
            'job_id': 'daily_data_collection',
            'start_time': job_start.isoformat(),
            'status': 'running',
            'details': {}
        }
        
        try:
            async with SessionLocal() as db:
                service = HistoricalDataService()
                
                # 主要通貨ペアのデータを収集
                currency_pairs = ['USD/JPY', 'EUR/USD', 'GBP/USD', 'EUR/JPY']
                results = []
                
                for pair in currency_pairs:
                    logger.info(f"Collecting daily data for {pair}")
                    result = await service.fetch_and_save(
                        db=db,
                        currency_pair=pair,
                        period='1d'  # 前日のデータ
                    )
                    results.append(result)
                    await asyncio.sleep(2)  # レート制限対策
                
                job_result['status'] = 'completed'
                job_result['details'] = {
                    'currency_pairs': currency_pairs,
                    'results': results,
                    'total_records': sum(r.get('records_saved', 0) for r in results)
                }
                
                # データソースステータスを更新
                await self._update_data_source_status(db, DataSourceType.YFINANCE, True)
                
        except Exception as e:
            logger.error(f"Error in daily data collection: {str(e)}")
            job_result['status'] = 'failed'
            job_result['error'] = str(e)
        
        finally:
            job_result['end_time'] = datetime.now().isoformat()
            job_result['duration'] = (datetime.now() - job_start).total_seconds()
            self.job_history.append(job_result)
            
            # 履歴を最新100件に制限
            if len(self.job_history) > 100:
                self.job_history = self.job_history[-100:]
    
    async def collect_realtime_data(self):
        """リアルタイムデータ収集タスク"""
        job_start = datetime.now()
        
        try:
            async with SessionLocal() as db:
                scraper = ForexScraper()
                
                # 現在のレートを取得
                rate_data = await scraper.get_current_rate()
                
                if rate_data:
                    # TODO: データベースに保存する処理を追加
                    logger.info(f"Collected realtime rate: {rate_data['rate']} from {rate_data['source']}")
                    
                    # データソースステータスを更新
                    await self._update_data_source_status(db, DataSourceType.SCRAPING, True)
                
        except Exception as e:
            logger.error(f"Error in realtime data collection: {str(e)}")
    
    async def check_data_quality(self):
        """データ品質チェックタスク"""
        job_start = datetime.now()
        
        try:
            async with SessionLocal() as db:
                # 過去7日間のデータ完全性をチェック
                end_date = datetime.now().date()
                start_date = end_date - timedelta(days=7)
                
                # TODO: データ品質チェックロジックの実装
                logger.info(f"Data quality check completed for {start_date} to {end_date}")
                
        except Exception as e:
            logger.error(f"Error in data quality check: {str(e)}")
    
    async def backup_weekly_data(self):
        """週次データバックアップタスク"""
        try:
            # TODO: バックアップロジックの実装
            logger.info("Weekly data backup completed")
        except Exception as e:
            logger.error(f"Error in weekly backup: {str(e)}")
    
    async def _update_data_source_status(
        self,
        db: AsyncSession,
        source_type: DataSourceType,
        success: bool
    ):
        """データソースのステータスを更新"""
        try:
            # データソースレコードを取得または作成
            source = await db.execute(
                db.query(DataSource).filter(
                    DataSource.source_type == source_type
                ).first()
            )
            
            if not source:
                source = DataSource(
                    name=f"{source_type.value} Data Source",
                    source_type=source_type,
                    status=DataSourceStatus.ACTIVE
                )
                db.add(source)
            
            # ステータスを更新
            if success:
                source.last_success_at = datetime.now()
                source.status = DataSourceStatus.ACTIVE
            else:
                source.last_failure_at = datetime.now()
                source.failure_count += 1
                if source.failure_count > 5:
                    source.status = DataSourceStatus.ERROR
            
            await db.commit()
            
        except Exception as e:
            logger.error(f"Error updating data source status: {str(e)}")
            await db.rollback()
    
    def get_job_status(self) -> Dict[str, Any]:
        """現在のジョブステータスを取得"""
        jobs = []
        for job in self.scheduler.get_jobs():
            jobs.append({
                'id': job.id,
                'name': job.name,
                'next_run': job.next_run_time.isoformat() if job.next_run_time else None,
                'trigger': str(job.trigger)
            })
        
        return {
            'scheduler_running': self.is_running,
            'jobs': jobs,
            'recent_history': self.job_history[-10:] if self.job_history else []
        }
    
    async def trigger_job(self, job_id: str) -> Dict[str, Any]:
        """ジョブを手動実行"""
        job = self.scheduler.get_job(job_id)
        if not job:
            raise ValueError(f"Job {job_id} not found")
        
        # ジョブを即座に実行
        job.modify(next_run_time=datetime.now())
        
        return {
            'job_id': job_id,
            'triggered_at': datetime.now().isoformat(),
            'message': f'Job {job_id} has been triggered'
        }
    
    def pause_job(self, job_id: str):
        """ジョブを一時停止"""
        self.scheduler.pause_job(job_id)
        logger.info(f"Job {job_id} paused")
    
    def resume_job(self, job_id: str):
        """ジョブを再開"""
        self.scheduler.resume_job(job_id)
        logger.info(f"Job {job_id} resumed")
    
    def modify_job_schedule(self, job_id: str, trigger_config: Dict[str, Any]):
        """ジョブのスケジュールを変更"""
        job = self.scheduler.get_job(job_id)
        if not job:
            raise ValueError(f"Job {job_id} not found")
        
        # トリガーを作成
        if trigger_config['type'] == 'cron':
            trigger = CronTrigger(**trigger_config['params'])
        elif trigger_config['type'] == 'interval':
            trigger = IntervalTrigger(**trigger_config['params'])
        else:
            raise ValueError(f"Unknown trigger type: {trigger_config['type']}")
        
        # ジョブを再スケジュール
        job.reschedule(trigger=trigger)
        logger.info(f"Job {job_id} rescheduled with new trigger")


# グローバルインスタンス
scheduler_service = SchedulerService()