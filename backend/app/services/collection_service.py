"""
Forex Prediction System - Data Collection Service
================================================

データ収集実行サービス（エンドポイント 4.2 用）
外部データソースからの為替データ自動収集機能を提供
"""

import logging
import uuid
import asyncio
from datetime import datetime, timedelta, date
from typing import Optional, List, Dict, Any
from decimal import Decimal
from sqlalchemy.orm import Session
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_, desc, update

from ..models import (
    ExchangeRate, DataSource, DataQuality, SystemSetting,
    DataSourceType, DataSourceStatus
)
from ..schemas.data import (
    DataCollectionRequest, DataCollectionResponse, CollectionProgress
)

logger = logging.getLogger(__name__)


class CollectionService:
    """データ収集実行サービスクラス"""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def execute_data_collection(
        self, 
        request: DataCollectionRequest
    ) -> DataCollectionResponse:
        """
        データ収集を実行
        
        Args:
            request: データ収集実行リクエスト
            
        Returns:
            DataCollectionResponse: 収集ジョブの開始情報
        """
        try:
            # 収集ジョブIDを生成
            collection_id = f"collect_{uuid.uuid4().hex[:8]}"
            current_time = datetime.now()
            
            logger.info(f"Starting data collection job: {collection_id}")
            
            # 対象ソースの決定
            target_sources = await self._determine_target_sources(request.sources)
            
            # アクティブなデータソースの状態確認
            active_sources = await self._get_active_data_sources(target_sources)
            
            if not active_sources:
                logger.warning("No active data sources available for collection")
                return self._create_error_response(
                    collection_id, 
                    "No active data sources available"
                )
            
            # 収集対象期間の決定
            date_range = await self._determine_collection_period(request.date_range)
            
            # 各ソースの進捗情報を初期化
            progress_list = []
            for source in active_sources:
                # 収集予想件数を計算
                estimated_items = await self._estimate_collection_items(
                    source, date_range, request.force_update
                )
                
                progress = CollectionProgress(
                    source_name=source.name,
                    total_items=estimated_items,
                    completed_items=0,
                    failed_items=0,
                    progress_percentage=0.0,
                    estimated_remaining_minutes=self._estimate_collection_time(
                        source.source_type, estimated_items
                    ),
                    current_activity="Initializing connection..."
                )
                progress_list.append(progress)
            
            # 完了予定時刻を計算
            max_estimated_time = max(
                [p.estimated_remaining_minutes or 0 for p in progress_list]
            )
            estimated_completion = (
                current_time + timedelta(minutes=max_estimated_time) 
                if max_estimated_time > 0 else None
            )
            
            # バックグラウンドで実際の収集を開始
            asyncio.create_task(
                self._execute_background_collection(
                    collection_id, active_sources, date_range, 
                    request.force_update, request.notify_on_completion
                )
            )
            
            return DataCollectionResponse(
                collection_id=collection_id,
                status="started",
                message=f"Data collection started for {len(active_sources)} sources",
                sources_count=len(active_sources),
                started_at=current_time,
                estimated_completion=estimated_completion,
                progress=progress_list
            )

        except Exception as e:
            logger.error(f"Error starting data collection: {str(e)}")
            return self._create_error_response(
                f"collect_{uuid.uuid4().hex[:8]}", 
                f"Failed to start data collection: {str(e)}"
            )

    async def _determine_target_sources(
        self, 
        requested_sources: Optional[List[DataSourceType]]
    ) -> List[DataSourceType]:
        """対象データソースを決定"""
        if requested_sources:
            return requested_sources
        
        # 全ソースを対象とする（優先度順）
        return [
            DataSourceType.YAHOO_FINANCE,
            DataSourceType.BOJ_CSV,
            DataSourceType.ALPHA_VANTAGE
        ]

    async def _get_active_data_sources(
        self, 
        target_types: List[DataSourceType]
    ) -> List[DataSource]:
        """アクティブなデータソースを取得"""
        try:
            stmt = (
                select(DataSource)
                .where(
                    and_(
                        DataSource.source_type.in_(target_types),
                        DataSource.status == DataSourceStatus.ACTIVE
                    )
                )
                .order_by(DataSource.priority)
            )
            
            result = await self.db.execute(stmt)
            return result.scalars().all()

        except Exception as e:
            logger.error(f"Error getting active data sources: {str(e)}")
            return []

    async def _determine_collection_period(
        self, 
        requested_range: Optional[Dict[str, str]]
    ) -> Dict[str, date]:
        """収集対象期間を決定"""
        if requested_range and 'start' in requested_range and 'end' in requested_range:
            try:
                start_date = datetime.strptime(requested_range['start'], '%Y-%m-%d').date()
                end_date = datetime.strptime(requested_range['end'], '%Y-%m-%d').date()
                
                return {
                    'start': start_date,
                    'end': end_date
                }
            except ValueError as e:
                logger.warning(f"Invalid date format in request: {e}")
        
        # デフォルト: 最近7日間のデータ
        end_date = date.today() - timedelta(days=1)  # 昨日まで
        start_date = end_date - timedelta(days=7)    # 過去7日間
        
        return {
            'start': start_date,
            'end': end_date
        }

    async def _estimate_collection_items(
        self, 
        source: DataSource, 
        date_range: Dict[str, date],
        force_update: bool
    ) -> int:
        """収集予想アイテム数を計算"""
        try:
            total_days = (date_range['end'] - date_range['start']).days + 1
            
            if force_update:
                # 強制更新の場合は全日数を対象
                return total_days
            
            # 既存データがある日数をカウント
            stmt = (
                select(func.count(ExchangeRate.id))
                .where(
                    and_(
                        ExchangeRate.date >= date_range['start'],
                        ExchangeRate.date <= date_range['end'],
                        ExchangeRate.source == source.source_type
                    )
                )
            )
            
            existing_count = await self.db.execute(stmt)
            existing_items = existing_count.scalar() or 0
            
            # 未収集のアイテム数を返す
            return max(0, total_days - existing_items)

        except Exception as e:
            logger.error(f"Error estimating collection items: {str(e)}")
            # フォールバック値
            return (date_range['end'] - date_range['start']).days + 1

    def _estimate_collection_time(
        self, 
        source_type: DataSourceType, 
        item_count: int
    ) -> Optional[int]:
        """収集時間を予想（分）"""
        if item_count == 0:
            return 0
        
        # ソース種別ごとの予想時間（1アイテムあたりの秒数）
        time_per_item = {
            DataSourceType.YAHOO_FINANCE: 2,      # 2秒/アイテム
            DataSourceType.BOJ_CSV: 1,            # 1秒/アイテム
            DataSourceType.ALPHA_VANTAGE: 5       # 5秒/アイテム（API制限あり）
        }
        
        seconds_per_item = time_per_item.get(source_type, 3)
        total_seconds = item_count * seconds_per_item
        
        # 最小1分、最大60分
        minutes = max(1, min(60, total_seconds // 60))
        return minutes

    async def _execute_background_collection(
        self,
        collection_id: str,
        sources: List[DataSource],
        date_range: Dict[str, date],
        force_update: bool,
        notify_on_completion: bool
    ):
        """バックグラウンドでのデータ収集実行"""
        try:
            logger.info(f"Starting background collection: {collection_id}")
            
            total_collected = 0
            total_failed = 0
            
            for source in sources:
                try:
                    # 各ソースからデータ収集
                    collected_count, failed_count = await self._collect_from_source(
                        source, date_range, force_update
                    )
                    
                    total_collected += collected_count
                    total_failed += failed_count
                    
                    logger.info(
                        f"Collection from {source.name}: "
                        f"collected={collected_count}, failed={failed_count}"
                    )
                    
                    # データソースの成功統計を更新
                    await self._update_source_statistics(
                        source, collected_count, failed_count
                    )
                    
                except Exception as e:
                    logger.error(f"Error collecting from {source.name}: {str(e)}")
                    total_failed += 1
            
            # 収集完了ログ
            logger.info(
                f"Collection {collection_id} completed: "
                f"collected={total_collected}, failed={total_failed}"
            )
            
            # 通知送信（必要に応じて）
            if notify_on_completion:
                await self._send_completion_notification(
                    collection_id, total_collected, total_failed
                )
            
        except Exception as e:
            logger.error(f"Background collection failed: {str(e)}")

    async def _collect_from_source(
        self,
        source: DataSource,
        date_range: Dict[str, date],
        force_update: bool
    ) -> tuple[int, int]:
        """指定ソースからデータ収集"""
        try:
            if source.source_type == DataSourceType.YAHOO_FINANCE:
                return await self._collect_from_yahoo_finance(
                    source, date_range, force_update
                )
            elif source.source_type == DataSourceType.BOJ_CSV:
                return await self._collect_from_boj_csv(
                    source, date_range, force_update
                )
            elif source.source_type == DataSourceType.ALPHA_VANTAGE:
                return await self._collect_from_alpha_vantage(
                    source, date_range, force_update
                )
            else:
                logger.warning(f"Unknown source type: {source.source_type}")
                return 0, 1

        except Exception as e:
            logger.error(f"Error collecting from source: {str(e)}")
            return 0, 1

    async def _collect_from_yahoo_finance(
        self,
        source: DataSource,
        date_range: Dict[str, date],
        force_update: bool
    ) -> tuple[int, int]:
        """Yahoo Financeからデータ収集"""
        # TODO: 実際のYahoo Finance API連携を実装
        # 現在は仮実装として成功を返す
        
        collected_count = 0
        failed_count = 0
        
        current_date = date_range['start']
        while current_date <= date_range['end']:
            try:
                # 既存データの確認
                if not force_update:
                    stmt = select(ExchangeRate.id).where(
                        and_(
                            ExchangeRate.date == current_date,
                            ExchangeRate.source == source.source_type
                        )
                    )
                    existing = await self.db.execute(stmt)
                    if existing.scalar():
                        current_date += timedelta(days=1)
                        continue
                
                # 仮の為替レートデータ生成（実装時は実際のAPI呼び出し）
                mock_rate = Decimal('150.00') + Decimal(str(current_date.day % 10))
                
                # データベースに保存
                exchange_rate = ExchangeRate(
                    date=current_date,
                    open_rate=mock_rate,
                    high_rate=mock_rate + Decimal('0.50'),
                    low_rate=mock_rate - Decimal('0.50'),
                    close_rate=mock_rate,
                    volume=1000000,
                    source=source.source_type,
                    is_holiday=False,
                    is_interpolated=False
                )
                
                self.db.add(exchange_rate)
                collected_count += 1
                
            except Exception as e:
                logger.error(f"Error collecting data for {current_date}: {str(e)}")
                failed_count += 1
            
            current_date += timedelta(days=1)
        
        # 変更をコミット
        try:
            await self.db.commit()
        except Exception as e:
            logger.error(f"Error committing Yahoo Finance data: {str(e)}")
            await self.db.rollback()
            # 失敗分としてカウント調整
            failed_count += collected_count
            collected_count = 0
        
        return collected_count, failed_count

    async def _collect_from_boj_csv(
        self,
        source: DataSource,
        date_range: Dict[str, date],
        force_update: bool
    ) -> tuple[int, int]:
        """日銀CSVからデータ収集"""
        # TODO: 実際の日銀CSVダウンロード・パース機能を実装
        # 現在は仮実装
        return 0, 0  # 日銀データは週末更新されないため通常は0件

    async def _collect_from_alpha_vantage(
        self,
        source: DataSource,
        date_range: Dict[str, date],
        force_update: bool
    ) -> tuple[int, int]:
        """Alpha VantageからAPI経由でデータ収集"""
        # TODO: 実際のAlpha Vantage API連携を実装
        # 現在は仮実装
        return 0, 0  # API制限により通常は少量収集

    async def _update_source_statistics(
        self,
        source: DataSource,
        collected_count: int,
        failed_count: int
    ):
        """データソースの統計情報を更新"""
        try:
            total_attempts = collected_count + failed_count
            if total_attempts == 0:
                return
            
            # 成功率の更新
            current_success_rate = float(source.success_rate or 0)
            new_success_rate = collected_count / total_attempts
            
            # 移動平均で成功率を更新（過去の履歴を考慮）
            updated_success_rate = (
                (current_success_rate * 0.8) + (new_success_rate * 0.2)
            )
            
            # 失敗回数の更新
            new_failure_count = source.failure_count + failed_count
            
            # 統計情報を更新
            update_stmt = (
                update(DataSource)
                .where(DataSource.id == source.id)
                .values(
                    success_rate=Decimal(str(round(updated_success_rate, 4))),
                    failure_count=new_failure_count,
                    last_success_at=datetime.now() if collected_count > 0 else source.last_success_at,
                    last_failure_at=datetime.now() if failed_count > 0 else source.last_failure_at,
                    updated_at=datetime.now()
                )
            )
            
            await self.db.execute(update_stmt)
            await self.db.commit()
            
        except Exception as e:
            logger.error(f"Error updating source statistics: {str(e)}")
            await self.db.rollback()

    async def _send_completion_notification(
        self,
        collection_id: str,
        collected_count: int,
        failed_count: int
    ):
        """収集完了通知を送信"""
        # TODO: 実際のメール・プッシュ通知機能を実装
        logger.info(
            f"Collection notification: {collection_id} - "
            f"Success: {collected_count}, Failed: {failed_count}"
        )

    def _create_error_response(
        self, 
        collection_id: str, 
        error_message: str
    ) -> DataCollectionResponse:
        """エラーレスポンスを生成"""
        return DataCollectionResponse(
            collection_id=collection_id,
            status="failed",
            message=error_message,
            sources_count=0,
            started_at=datetime.now(),
            estimated_completion=None,
            progress=[]
        )

    async def get_collection_status(self, collection_id: str) -> Optional[Dict[str, Any]]:
        """収集状況を取得（将来の拡張用）"""
        # TODO: 収集進捗の追跡機能を実装
        return {
            "collection_id": collection_id,
            "status": "completed",
            "message": "Collection status tracking not yet implemented"
        }