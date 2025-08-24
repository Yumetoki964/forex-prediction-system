"""
データ差分更新サービス - 効率的なデータ更新管理
"""
import logging
from datetime import datetime, timedelta, date
from typing import Optional, Dict, Any, List, Tuple
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, or_, func
import pandas as pd

from app.models import ExchangeRate, DataSourceType
from app.services.historical_data_service import HistoricalDataService

logger = logging.getLogger(__name__)


class DataUpdateService:
    """データ差分更新管理サービス"""
    
    def __init__(self):
        self.historical_service = HistoricalDataService()
        
    async def get_data_gaps(
        self,
        db: AsyncSession,
        currency_pair: str = 'USD/JPY',
        start_date: Optional[date] = None,
        end_date: Optional[date] = None
    ) -> List[Dict[str, Any]]:
        """
        データの欠損期間を検出
        
        Args:
            db: データベースセッション
            currency_pair: 通貨ペア
            start_date: 開始日
            end_date: 終了日
        
        Returns:
            欠損期間のリスト
        """
        try:
            # デフォルト期間（過去1年）
            if not end_date:
                end_date = datetime.now().date()
            if not start_date:
                start_date = end_date - timedelta(days=365)
            
            # 既存データの日付を取得
            query = select(ExchangeRate.date).where(
                and_(
                    ExchangeRate.date >= start_date,
                    ExchangeRate.date <= end_date
                )
            ).order_by(ExchangeRate.date)
            
            result = await db.execute(query)
            existing_dates = {row[0] for row in result}
            
            # 期待される営業日を生成（土日を除く）
            expected_dates = set()
            current = start_date
            while current <= end_date:
                if current.weekday() < 5:  # 月曜日(0)から金曜日(4)
                    expected_dates.add(current)
                current += timedelta(days=1)
            
            # 欠損日を特定
            missing_dates = expected_dates - existing_dates
            
            if not missing_dates:
                return []
            
            # 連続する欠損期間をグループ化
            gaps = self._group_consecutive_dates(sorted(missing_dates))
            
            return [
                {
                    'start_date': gap[0].isoformat(),
                    'end_date': gap[-1].isoformat(),
                    'days': len(gap),
                    'dates': [d.isoformat() for d in gap]
                }
                for gap in gaps
            ]
            
        except Exception as e:
            logger.error(f"Error detecting data gaps: {str(e)}")
            raise
    
    def _group_consecutive_dates(self, dates: List[date]) -> List[List[date]]:
        """連続する日付をグループ化"""
        if not dates:
            return []
        
        groups = []
        current_group = [dates[0]]
        
        for i in range(1, len(dates)):
            if dates[i] - dates[i-1] == timedelta(days=1):
                current_group.append(dates[i])
            else:
                groups.append(current_group)
                current_group = [dates[i]]
        
        groups.append(current_group)
        return groups
    
    async def fill_data_gaps(
        self,
        db: AsyncSession,
        currency_pair: str = 'USD/JPY',
        max_days: int = 30
    ) -> Dict[str, Any]:
        """
        データの欠損を埋める
        
        Args:
            db: データベースセッション
            currency_pair: 通貨ペア
            max_days: 一度に取得する最大日数
        
        Returns:
            更新結果
        """
        try:
            # 欠損期間を検出
            gaps = await self.get_data_gaps(db, currency_pair)
            
            if not gaps:
                return {
                    'status': 'no_gaps',
                    'message': 'No data gaps found',
                    'gaps_filled': 0
                }
            
            filled_count = 0
            filled_periods = []
            
            for gap in gaps:
                gap_start = datetime.fromisoformat(gap['start_date']).date()
                gap_end = datetime.fromisoformat(gap['end_date']).date()
                gap_days = (gap_end - gap_start).days + 1
                
                # 大きなギャップは分割して処理
                if gap_days > max_days:
                    current = gap_start
                    while current <= gap_end:
                        chunk_end = min(current + timedelta(days=max_days-1), gap_end)
                        
                        # データを取得して保存
                        result = await self._fetch_and_save_period(
                            db, currency_pair, current, chunk_end
                        )
                        
                        if result['records_saved'] > 0:
                            filled_count += result['records_saved']
                            filled_periods.append({
                                'start': current.isoformat(),
                                'end': chunk_end.isoformat(),
                                'records': result['records_saved']
                            })
                        
                        current = chunk_end + timedelta(days=1)
                else:
                    # 小さなギャップは一度に処理
                    result = await self._fetch_and_save_period(
                        db, currency_pair, gap_start, gap_end
                    )
                    
                    if result['records_saved'] > 0:
                        filled_count += result['records_saved']
                        filled_periods.append({
                            'start': gap_start.isoformat(),
                            'end': gap_end.isoformat(),
                            'records': result['records_saved']
                        })
            
            return {
                'status': 'success',
                'message': f'Filled {filled_count} missing records',
                'gaps_detected': len(gaps),
                'gaps_filled': len(filled_periods),
                'filled_periods': filled_periods,
                'total_records': filled_count
            }
            
        except Exception as e:
            logger.error(f"Error filling data gaps: {str(e)}")
            return {
                'status': 'error',
                'message': str(e),
                'gaps_filled': 0
            }
    
    async def _fetch_and_save_period(
        self,
        db: AsyncSession,
        currency_pair: str,
        start_date: date,
        end_date: date
    ) -> Dict[str, Any]:
        """特定期間のデータを取得して保存"""
        try:
            # yfinanceでデータ取得
            data = await self.historical_service.fetch_historical_data(
                currency_pair=currency_pair,
                start_date=start_date,
                end_date=end_date
            )
            
            if data.empty:
                return {'records_saved': 0}
            
            # データベースに保存
            records_saved = await self.historical_service.save_to_database(
                db, data, currency_pair
            )
            
            return {'records_saved': records_saved}
            
        except Exception as e:
            logger.error(f"Error fetching period {start_date} to {end_date}: {str(e)}")
            return {'records_saved': 0}
    
    async def update_latest_data(
        self,
        db: AsyncSession,
        currency_pairs: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        最新データを更新（過去3日分）
        
        Args:
            db: データベースセッション
            currency_pairs: 更新する通貨ペアのリスト
        
        Returns:
            更新結果
        """
        try:
            if not currency_pairs:
                currency_pairs = ['USD/JPY', 'EUR/USD', 'GBP/USD', 'EUR/JPY']
            
            results = []
            total_updated = 0
            
            for pair in currency_pairs:
                # 過去3日分のデータを取得
                result = await self.historical_service.fetch_and_save(
                    db=db,
                    currency_pair=pair,
                    period='5d'  # 週末を考慮して5日分
                )
                
                results.append({
                    'pair': pair,
                    'status': result['status'],
                    'records': result.get('records_saved', 0)
                })
                
                total_updated += result.get('records_saved', 0)
            
            return {
                'status': 'success',
                'message': f'Updated {total_updated} records',
                'currency_pairs': results,
                'total_records': total_updated,
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error updating latest data: {str(e)}")
            return {
                'status': 'error',
                'message': str(e),
                'total_records': 0
            }
    
    async def get_update_statistics(
        self,
        db: AsyncSession,
        days: int = 30
    ) -> Dict[str, Any]:
        """
        データ更新統計を取得
        
        Args:
            db: データベースセッション
            days: 統計期間（日数）
        
        Returns:
            更新統計情報
        """
        try:
            since_date = datetime.now().date() - timedelta(days=days)
            
            # 各データソースごとの統計を取得
            stats = {}
            
            for source_type in [DataSourceType.YFINANCE, DataSourceType.SCRAPING]:
                query = select(
                    func.count(ExchangeRate.id).label('count'),
                    func.min(ExchangeRate.date).label('min_date'),
                    func.max(ExchangeRate.date).label('max_date'),
                    func.min(ExchangeRate.created_at).label('first_created'),
                    func.max(ExchangeRate.created_at).label('last_created')
                ).where(
                    and_(
                        ExchangeRate.source == source_type,
                        ExchangeRate.created_at >= datetime.now() - timedelta(days=days)
                    )
                )
                
                result = await db.execute(query)
                row = result.first()
                
                if row and row.count > 0:
                    stats[source_type.value] = {
                        'records_count': row.count,
                        'date_range': {
                            'start': row.min_date.isoformat() if row.min_date else None,
                            'end': row.max_date.isoformat() if row.max_date else None
                        },
                        'update_times': {
                            'first': row.first_created.isoformat() if row.first_created else None,
                            'last': row.last_created.isoformat() if row.last_created else None
                        }
                    }
            
            # 全体の統計
            total_query = select(
                func.count(ExchangeRate.id).label('total'),
                func.count(func.distinct(ExchangeRate.date)).label('unique_days')
            ).where(
                ExchangeRate.created_at >= datetime.now() - timedelta(days=days)
            )
            
            total_result = await db.execute(total_query)
            total_row = total_result.first()
            
            return {
                'period_days': days,
                'total_records': total_row.total if total_row else 0,
                'unique_days': total_row.unique_days if total_row else 0,
                'sources': stats,
                'last_check': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error getting update statistics: {str(e)}")
            return {
                'period_days': days,
                'total_records': 0,
                'error': str(e)
            }
    
    async def validate_data_integrity(
        self,
        db: AsyncSession,
        currency_pair: str = 'USD/JPY',
        days: int = 30
    ) -> Dict[str, Any]:
        """
        データの整合性を検証
        
        Args:
            db: データベースセッション
            currency_pair: 通貨ペア
            days: 検証期間（日数）
        
        Returns:
            検証結果
        """
        try:
            since_date = datetime.now().date() - timedelta(days=days)
            
            # データを取得
            query = select(ExchangeRate).where(
                ExchangeRate.date >= since_date
            ).order_by(ExchangeRate.date)
            
            result = await db.execute(query)
            records = result.scalars().all()
            
            issues = []
            
            # 各種チェック
            for i, record in enumerate(records):
                # 1. OHLC関係性チェック
                if record.high_rate < record.low_rate:
                    issues.append({
                        'date': record.date.isoformat(),
                        'type': 'invalid_ohlc',
                        'message': f'High ({record.high_rate}) < Low ({record.low_rate})'
                    })
                
                # 2. 異常値チェック（前日比50%以上の変動）
                if i > 0:
                    prev_record = records[i-1]
                    change_pct = abs((record.close_rate - prev_record.close_rate) / prev_record.close_rate) * 100
                    
                    if change_pct > 50:
                        issues.append({
                            'date': record.date.isoformat(),
                            'type': 'extreme_change',
                            'message': f'Change of {change_pct:.2f}% from previous day'
                        })
                
                # 3. 負の値チェック
                if any(val < 0 for val in [record.open_rate, record.high_rate, record.low_rate, record.close_rate] if val):
                    issues.append({
                        'date': record.date.isoformat(),
                        'type': 'negative_value',
                        'message': 'Negative rate value detected'
                    })
            
            return {
                'status': 'completed',
                'records_checked': len(records),
                'issues_found': len(issues),
                'issues': issues[:50],  # 最初の50件のみ返す
                'integrity_score': max(0, 100 - len(issues)) if records else 100
            }
            
        except Exception as e:
            logger.error(f"Error validating data integrity: {str(e)}")
            return {
                'status': 'error',
                'message': str(e),
                'issues_found': 0
            }