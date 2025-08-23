"""
Forex Prediction System - Data Repair Service
=============================================

欠損データ修復サービス（エンドポイント 4.4 用）
データ品質問題の自動修復・補間機能を提供
"""

import logging
import uuid
import asyncio
from datetime import datetime, timedelta, date
from typing import Optional, List, Dict, Any, Tuple
from decimal import Decimal
from sqlalchemy.orm import Session
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_, desc, update, insert, text
import json

from ..models import (
    ExchangeRate, DataQuality, DataSource,
    DataSourceType, DataSourceStatus
)
from ..schemas.data import (
    DataRepairRequest, DataRepairResponse, RepairTarget,
    RepairResult, RepairAction
)

logger = logging.getLogger(__name__)


class RepairService:
    """欠損データ修復サービスクラス"""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def execute_data_repair(
        self, 
        request: DataRepairRequest
    ) -> DataRepairResponse:
        """
        欠損データ修復を実行
        
        Args:
            request: データ修復実行リクエスト
            
        Returns:
            DataRepairResponse: 修復ジョブの実行結果
        """
        try:
            repair_id = f"repair_{uuid.uuid4().hex[:8]}"
            current_time = datetime.now()
            
            logger.info(f"Starting data repair job: {repair_id} (dry_run: {request.dry_run})")
            
            # 修復対象の検証
            validated_targets = await self._validate_repair_targets(request.repair_targets)
            
            if not validated_targets:
                return self._create_error_response(
                    repair_id,
                    "No valid repair targets found"
                )
            
            # 全体対象期間の計算
            all_start_dates = [target.date_range["start"] for target in validated_targets]
            all_end_dates = [target.date_range["end"] for target in validated_targets]
            total_date_range = {
                "start": min(all_start_dates),
                "end": max(all_end_dates)
            }
            
            # 修復時間の見積もり
            estimated_minutes = await self._estimate_repair_time(validated_targets)
            estimated_completion = current_time + timedelta(minutes=estimated_minutes)
            
            # 修復前バックアップ作成（dry_runでない場合）
            if not request.dry_run and request.backup_before_repair:
                await self._create_repair_backup(total_date_range)
            
            # 実際の修復実行
            repair_results, errors, warnings = await self._execute_repair_targets(
                validated_targets, request.repair_strategy, request.dry_run
            )
            
            # 完了時間とメッセージ
            completed_at = datetime.now()
            execution_time = int((completed_at - current_time).total_seconds())
            
            status_message = (
                "Data repair completed in dry-run mode" if request.dry_run
                else "Data repair completed successfully"
            )
            
            if errors:
                status_message = "Data repair completed with errors"
            
            return DataRepairResponse(
                repair_id=repair_id,
                status="completed",
                is_dry_run=request.dry_run,
                message=status_message,
                started_at=current_time,
                estimated_completion=estimated_completion,
                targets_count=len(validated_targets),
                total_date_range=total_date_range,
                repair_results=repair_results,
                errors=errors,
                warnings=warnings,
                completed_at=completed_at,
                total_execution_time=execution_time
            )

        except Exception as e:
            logger.error(f"Error executing data repair: {str(e)}")
            return self._create_error_response(
                f"repair_{uuid.uuid4().hex[:8]}",
                f"Data repair failed: {str(e)}"
            )

    async def _validate_repair_targets(
        self, 
        targets: List[RepairTarget]
    ) -> List[RepairTarget]:
        """修復対象の妥当性を検証"""
        validated_targets = []
        
        for target in targets:
            try:
                start_date = target.date_range["start"]
                end_date = target.date_range["end"]
                
                # 日付の妥当性チェック
                if start_date >= end_date:
                    logger.warning(f"Invalid date range: {start_date} >= {end_date}")
                    continue
                
                # 未来の日付チェック
                if start_date > date.today():
                    logger.warning(f"Future date range specified: {start_date}")
                    continue
                
                # 期間の長さチェック（最大1年間）
                if (end_date - start_date).days > 365:
                    logger.warning(f"Repair period too long: {(end_date - start_date).days} days")
                    # 1年間に制限
                    target.date_range["end"] = start_date + timedelta(days=365)
                
                validated_targets.append(target)
                
            except Exception as e:
                logger.error(f"Error validating repair target: {str(e)}")
                continue
        
        return validated_targets

    async def _estimate_repair_time(self, targets: List[RepairTarget]) -> int:
        """修復時間を見積もり（分）"""
        total_days = 0
        
        for target in targets:
            target_days = (target.date_range["end"] - target.date_range["start"]).days
            total_days += target_days
        
        # 基本時間：1日あたり2秒
        base_minutes = max(1, total_days * 2 // 60)
        
        # 最小5分、最大60分
        return max(5, min(60, base_minutes))

    async def _create_repair_backup(self, date_range: Dict[str, date]):
        """修復前のバックアップを作成"""
        try:
            backup_table_name = f"exchange_rates_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            
            backup_stmt = text(f"""
                CREATE TABLE {backup_table_name} AS
                SELECT * FROM exchange_rates
                WHERE date >= :start_date AND date <= :end_date
            """)
            
            await self.db.execute(
                backup_stmt,
                {"start_date": date_range["start"], "end_date": date_range["end"]}
            )
            
            await self.db.commit()
            logger.info(f"Created backup table: {backup_table_name}")
            
        except Exception as e:
            logger.error(f"Error creating backup: {str(e)}")
            raise

    async def _execute_repair_targets(
        self,
        targets: List[RepairTarget],
        repair_strategy: str,
        dry_run: bool
    ) -> Tuple[List[RepairResult], List[str], List[str]]:
        """修復対象を実行"""
        repair_results: List[RepairResult] = []
        errors: List[str] = []
        warnings: List[str] = []
        
        for target in targets:
            try:
                result, target_errors, target_warnings = await self._execute_single_target_repair(
                    target, repair_strategy, dry_run
                )
                
                repair_results.append(result)
                errors.extend(target_errors)
                warnings.extend(target_warnings)
                
            except Exception as e:
                error_msg = f"Failed to repair target {target.date_range}: {str(e)}"
                logger.error(error_msg)
                errors.append(error_msg)
        
        return repair_results, errors, warnings

    async def _execute_single_target_repair(
        self,
        target: RepairTarget,
        repair_strategy: str,
        dry_run: bool
    ) -> Tuple[RepairResult, List[str], List[str]]:
        """単一対象の修復を実行"""
        errors = []
        warnings = []
        repair_actions = []
        
        # 対象期間の問題を特定
        issues = await self._identify_issues_in_range(
            target.date_range["start"],
            target.date_range["end"],
            target.issue_types
        )
        
        total_issues_found = len(issues)
        issues_repaired = 0
        issues_skipped = 0
        
        for issue in issues:
            try:
                action = await self._create_repair_action(
                    issue, target, repair_strategy, dry_run
                )
                
                if action:
                    repair_actions.append(action)
                    issues_repaired += 1
                else:
                    issues_skipped += 1
                    
            except Exception as e:
                issues_skipped += 1
                errors.append(f"Failed to repair issue on {issue.get('date')}: {str(e)}")
        
        # 修復成功率と平均信頼度を計算
        repair_success_rate = issues_repaired / max(1, total_issues_found)
        avg_confidence_score = (
            sum(action.confidence_score for action in repair_actions) / max(1, len(repair_actions))
        )
        
        return RepairResult(
            target_range=target.date_range,
            total_issues_found=total_issues_found,
            issues_repaired=issues_repaired,
            issues_skipped=issues_skipped,
            repair_success_rate=repair_success_rate,
            avg_confidence_score=avg_confidence_score,
            repair_actions=repair_actions
        ), errors, warnings

    async def _identify_issues_in_range(
        self,
        start_date: date,
        end_date: date,
        issue_types: Optional[List[str]]
    ) -> List[Dict[str, Any]]:
        """指定期間の問題を特定"""
        issues = []
        
        # すべての問題タイプを検出（issue_typesが指定されていない場合）
        target_issue_types = issue_types or [
            "missing_data", "outlier_values", "duplicate_data", "inconsistent_data"
        ]
        
        if "missing_data" in target_issue_types:
            missing_issues = await self._find_missing_data_issues(start_date, end_date)
            issues.extend(missing_issues)
        
        if "outlier_values" in target_issue_types:
            outlier_issues = await self._find_outlier_value_issues(start_date, end_date)
            issues.extend(outlier_issues)
        
        if "duplicate_data" in target_issue_types:
            duplicate_issues = await self._find_duplicate_data_issues(start_date, end_date)
            issues.extend(duplicate_issues)
        
        if "inconsistent_data" in target_issue_types:
            inconsistent_issues = await self._find_inconsistent_data_issues(start_date, end_date)
            issues.extend(inconsistent_issues)
        
        return issues

    async def _find_missing_data_issues(
        self, 
        start_date: date, 
        end_date: date
    ) -> List[Dict[str, Any]]:
        """欠損データ問題を特定"""
        issues = []
        
        try:
            # 営業日で欠損している日付を取得
            missing_dates_stmt = text("""
                WITH RECURSIVE date_range AS (
                    SELECT :start_date::date as date
                    UNION ALL
                    SELECT date + INTERVAL '1 day'
                    FROM date_range
                    WHERE date < :end_date::date
                ),
                business_days AS (
                    SELECT date
                    FROM date_range
                    WHERE EXTRACT(DOW FROM date) NOT IN (0, 6)
                ),
                missing_days AS (
                    SELECT bd.date
                    FROM business_days bd
                    LEFT JOIN exchange_rates er ON bd.date = er.date
                    WHERE er.date IS NULL
                )
                SELECT date FROM missing_days ORDER BY date
            """)
            
            result = await self.db.execute(
                missing_dates_stmt,
                {"start_date": start_date, "end_date": end_date}
            )
            
            missing_dates = [row[0] for row in result.fetchall()]
            
            for missing_date in missing_dates:
                issues.append({
                    "type": "missing_data",
                    "date": missing_date,
                    "description": f"Missing exchange rate data for {missing_date}",
                    "severity": "medium",
                    "auto_repairable": True
                })
        
        except Exception as e:
            logger.error(f"Error finding missing data issues: {str(e)}")
        
        return issues

    async def _find_outlier_value_issues(
        self, 
        start_date: date, 
        end_date: date
    ) -> List[Dict[str, Any]]:
        """外れ値問題を特定"""
        issues = []
        
        try:
            # 統計的外れ値を検出
            outliers_stmt = text("""
                WITH rate_stats AS (
                    SELECT 
                        AVG(close_rate::numeric) as mean_rate,
                        STDDEV(close_rate::numeric) as std_dev
                    FROM exchange_rates
                    WHERE date >= :start_date AND date <= :end_date
                    AND close_rate IS NOT NULL
                ),
                outliers AS (
                    SELECT er.date, er.close_rate, er.id
                    FROM exchange_rates er
                    CROSS JOIN rate_stats rs
                    WHERE er.date >= :start_date AND er.date <= :end_date
                    AND er.close_rate IS NOT NULL
                    AND ABS(er.close_rate::numeric - rs.mean_rate) > 3 * rs.std_dev
                )
                SELECT date, close_rate, id FROM outliers ORDER BY date
            """)
            
            result = await self.db.execute(
                outliers_stmt,
                {"start_date": start_date, "end_date": end_date}
            )
            
            for row in result.fetchall():
                issues.append({
                    "type": "outlier_values",
                    "date": row[0],
                    "current_value": row[1],
                    "record_id": row[2],
                    "description": f"Outlier exchange rate value {row[1]} on {row[0]}",
                    "severity": "low",
                    "auto_repairable": True
                })
        
        except Exception as e:
            logger.error(f"Error finding outlier value issues: {str(e)}")
        
        return issues

    async def _find_duplicate_data_issues(
        self, 
        start_date: date, 
        end_date: date
    ) -> List[Dict[str, Any]]:
        """重複データ問題を特定"""
        issues = []
        
        try:
            # 同一日付の重複レコードを検出
            duplicates_stmt = text("""
                SELECT date, COUNT(*) as duplicate_count, 
                       array_agg(id ORDER BY id) as record_ids
                FROM exchange_rates
                WHERE date >= :start_date AND date <= :end_date
                GROUP BY date
                HAVING COUNT(*) > 1
                ORDER BY date
            """)
            
            result = await self.db.execute(
                duplicates_stmt,
                {"start_date": start_date, "end_date": end_date}
            )
            
            for row in result.fetchall():
                issues.append({
                    "type": "duplicate_data",
                    "date": row[0],
                    "duplicate_count": row[1],
                    "record_ids": row[2],
                    "description": f"Duplicate records found for date {row[0]} (count: {row[1]})",
                    "severity": "medium",
                    "auto_repairable": True
                })
        
        except Exception as e:
            logger.error(f"Error finding duplicate data issues: {str(e)}")
        
        return issues

    async def _find_inconsistent_data_issues(
        self, 
        start_date: date, 
        end_date: date
    ) -> List[Dict[str, Any]]:
        """データ整合性問題を特定"""
        issues = []
        
        try:
            # OHLC データの整合性をチェック（High >= Low, etc.）
            inconsistent_stmt = text("""
                SELECT date, id, open_rate, high_rate, low_rate, close_rate
                FROM exchange_rates
                WHERE date >= :start_date AND date <= :end_date
                AND (
                    high_rate < low_rate OR
                    high_rate < LEAST(open_rate, close_rate) OR
                    low_rate > GREATEST(open_rate, close_rate)
                )
                ORDER BY date
            """)
            
            result = await self.db.execute(
                inconsistent_stmt,
                {"start_date": start_date, "end_date": end_date}
            )
            
            for row in result.fetchall():
                issues.append({
                    "type": "inconsistent_data",
                    "date": row[0],
                    "record_id": row[1],
                    "ohlc_values": {
                        "open": row[2], "high": row[3], 
                        "low": row[4], "close": row[5]
                    },
                    "description": f"Inconsistent OHLC data on {row[0]}",
                    "severity": "high",
                    "auto_repairable": True
                })
        
        except Exception as e:
            logger.error(f"Error finding inconsistent data issues: {str(e)}")
        
        return issues

    async def _create_repair_action(
        self,
        issue: Dict[str, Any],
        target: RepairTarget,
        repair_strategy: str,
        dry_run: bool
    ) -> Optional[RepairAction]:
        """修復アクションを作成・実行"""
        try:
            issue_type = issue["type"]
            issue_date = issue["date"]
            
            if issue_type == "missing_data":
                return await self._repair_missing_data(issue, target, repair_strategy, dry_run)
            elif issue_type == "outlier_values":
                return await self._repair_outlier_values(issue, target, repair_strategy, dry_run)
            elif issue_type == "duplicate_data":
                return await self._repair_duplicate_data(issue, target, repair_strategy, dry_run)
            elif issue_type == "inconsistent_data":
                return await self._repair_inconsistent_data(issue, target, repair_strategy, dry_run)
            else:
                logger.warning(f"Unknown issue type: {issue_type}")
                return None

        except Exception as e:
            logger.error(f"Error creating repair action for {issue}: {str(e)}")
            return None

    async def _repair_missing_data(
        self,
        issue: Dict[str, Any],
        target: RepairTarget,
        repair_strategy: str,
        dry_run: bool
    ) -> Optional[RepairAction]:
        """欠損データを修復"""
        try:
            missing_date = issue["date"]
            
            # 周辺データを取得して補間値を計算
            interpolated_value, confidence, source_dates = await self._calculate_interpolated_value(
                missing_date, target.max_interpolation_gap
            )
            
            if not interpolated_value:
                return None
            
            # 実際のデータ挿入（dry_runでない場合）
            if not dry_run:
                await self._insert_interpolated_record(
                    missing_date, interpolated_value, source_dates
                )
            
            return RepairAction(
                action_type="interpolate",
                target_date=missing_date,
                original_value=None,
                repaired_value=interpolated_value,
                confidence_score=confidence,
                method_used="linear_interpolation",
                source_data_points=source_dates
            )

        except Exception as e:
            logger.error(f"Error repairing missing data: {str(e)}")
            return None

    async def _repair_outlier_values(
        self,
        issue: Dict[str, Any],
        target: RepairTarget,
        repair_strategy: str,
        dry_run: bool
    ) -> Optional[RepairAction]:
        """外れ値を修復"""
        try:
            outlier_date = issue["date"]
            original_value = Decimal(str(issue["current_value"]))
            record_id = issue["record_id"]
            
            # 周辺値から適切な値を計算
            corrected_value, confidence, source_dates = await self._calculate_outlier_correction(
                outlier_date, original_value
            )
            
            if not corrected_value:
                return None
            
            # 実際のデータ更新（dry_runでない場合）
            if not dry_run:
                await self._update_outlier_record(record_id, corrected_value)
            
            return RepairAction(
                action_type="outlier_correction",
                target_date=outlier_date,
                original_value=original_value,
                repaired_value=corrected_value,
                confidence_score=confidence,
                method_used="median_based_correction",
                source_data_points=source_dates
            )

        except Exception as e:
            logger.error(f"Error repairing outlier values: {str(e)}")
            return None

    async def _repair_duplicate_data(
        self,
        issue: Dict[str, Any],
        target: RepairTarget,
        repair_strategy: str,
        dry_run: bool
    ) -> Optional[RepairAction]:
        """重複データを修復"""
        try:
            duplicate_date = issue["date"]
            record_ids = issue["record_ids"]
            
            if len(record_ids) < 2:
                return None
            
            # 最も信頼性の高いレコードを選択（最新作成日時など）
            best_record_id = await self._select_best_duplicate_record(record_ids)
            
            # 重複レコードを削除（dry_runでない場合）
            removed_count = 0
            if not dry_run:
                removed_count = await self._remove_duplicate_records(
                    record_ids, best_record_id
                )
            
            return RepairAction(
                action_type="remove_duplicates",
                target_date=duplicate_date,
                original_value=Decimal(str(len(record_ids))),  # 元の重複数
                repaired_value=Decimal("1"),  # 修復後は1レコード
                confidence_score=0.95,
                method_used="keep_latest_created",
                source_data_points=[duplicate_date]
            )

        except Exception as e:
            logger.error(f"Error repairing duplicate data: {str(e)}")
            return None

    async def _repair_inconsistent_data(
        self,
        issue: Dict[str, Any],
        target: RepairTarget,
        repair_strategy: str,
        dry_run: bool
    ) -> Optional[RepairAction]:
        """データ整合性を修復"""
        try:
            inconsistent_date = issue["date"]
            record_id = issue["record_id"]
            ohlc_values = issue["ohlc_values"]
            
            # OHLC データの整合性を修正
            corrected_ohlc = self._correct_ohlc_consistency(ohlc_values)
            
            # 実際のデータ更新（dry_runでない場合）
            if not dry_run:
                await self._update_ohlc_record(record_id, corrected_ohlc)
            
            return RepairAction(
                action_type="correct_ohlc",
                target_date=inconsistent_date,
                original_value=Decimal(str(ohlc_values["close"])),
                repaired_value=Decimal(str(corrected_ohlc["close"])),
                confidence_score=0.90,
                method_used="ohlc_consistency_correction",
                source_data_points=[inconsistent_date]
            )

        except Exception as e:
            logger.error(f"Error repairing inconsistent data: {str(e)}")
            return None

    async def _calculate_interpolated_value(
        self,
        missing_date: date,
        max_gap: int
    ) -> Tuple[Optional[Decimal], float, List[date]]:
        """欠損値の補間を計算"""
        try:
            # 前後のデータを取得
            before_data = await self._get_data_before_date(missing_date, max_gap)
            after_data = await self._get_data_after_date(missing_date, max_gap)
            
            if not before_data or not after_data:
                return None, 0.0, []
            
            # 線形補間を実行
            before_date, before_rate = before_data
            after_date, after_rate = after_data
            
            total_days = (after_date - before_date).days
            missing_days = (missing_date - before_date).days
            
            if total_days == 0:
                return None, 0.0, []
            
            # 線形補間の計算
            weight = missing_days / total_days
            interpolated_rate = before_rate + (after_rate - before_rate) * Decimal(str(weight))
            
            # 信頼度の計算（ギャップが小さいほど高い）
            confidence = max(0.5, 1.0 - (total_days / (max_gap * 2)))
            
            return (
                Decimal(str(round(float(interpolated_rate), 4))),
                confidence,
                [before_date, after_date]
            )

        except Exception as e:
            logger.error(f"Error calculating interpolated value: {str(e)}")
            return None, 0.0, []

    async def _calculate_outlier_correction(
        self,
        outlier_date: date,
        original_value: Decimal
    ) -> Tuple[Optional[Decimal], float, List[date]]:
        """外れ値の修正値を計算"""
        try:
            # 周辺7日のデータを取得
            surrounding_data = await self._get_surrounding_data(outlier_date, 7)
            
            if len(surrounding_data) < 3:
                return None, 0.0, []
            
            # 中央値ベースの修正
            rates = [float(data[1]) for data in surrounding_data]
            median_rate = sorted(rates)[len(rates) // 2]
            
            corrected_value = Decimal(str(round(median_rate, 4)))
            
            # 信頼度（周辺データ数に依存）
            confidence = min(0.95, 0.5 + (len(surrounding_data) / 20))
            
            source_dates = [data[0] for data in surrounding_data]
            
            return corrected_value, confidence, source_dates

        except Exception as e:
            logger.error(f"Error calculating outlier correction: {str(e)}")
            return None, 0.0, []

    async def _get_data_before_date(
        self, 
        target_date: date, 
        max_days: int
    ) -> Optional[Tuple[date, Decimal]]:
        """指定日前のデータを取得"""
        try:
            stmt = (
                select(ExchangeRate.date, ExchangeRate.close_rate)
                .where(
                    and_(
                        ExchangeRate.date < target_date,
                        ExchangeRate.date >= target_date - timedelta(days=max_days),
                        ExchangeRate.close_rate.isnot(None)
                    )
                )
                .order_by(desc(ExchangeRate.date))
                .limit(1)
            )
            
            result = await self.db.execute(stmt)
            row = result.fetchone()
            
            return (row[0], row[1]) if row else None

        except Exception as e:
            logger.error(f"Error getting data before date: {str(e)}")
            return None

    async def _get_data_after_date(
        self, 
        target_date: date, 
        max_days: int
    ) -> Optional[Tuple[date, Decimal]]:
        """指定日後のデータを取得"""
        try:
            stmt = (
                select(ExchangeRate.date, ExchangeRate.close_rate)
                .where(
                    and_(
                        ExchangeRate.date > target_date,
                        ExchangeRate.date <= target_date + timedelta(days=max_days),
                        ExchangeRate.close_rate.isnot(None)
                    )
                )
                .order_by(ExchangeRate.date)
                .limit(1)
            )
            
            result = await self.db.execute(stmt)
            row = result.fetchone()
            
            return (row[0], row[1]) if row else None

        except Exception as e:
            logger.error(f"Error getting data after date: {str(e)}")
            return None

    async def _get_surrounding_data(
        self, 
        center_date: date, 
        days: int
    ) -> List[Tuple[date, Decimal]]:
        """指定日周辺のデータを取得"""
        try:
            stmt = (
                select(ExchangeRate.date, ExchangeRate.close_rate)
                .where(
                    and_(
                        ExchangeRate.date >= center_date - timedelta(days=days),
                        ExchangeRate.date <= center_date + timedelta(days=days),
                        ExchangeRate.date != center_date,
                        ExchangeRate.close_rate.isnot(None)
                    )
                )
                .order_by(ExchangeRate.date)
            )
            
            result = await self.db.execute(stmt)
            return [(row[0], row[1]) for row in result.fetchall()]

        except Exception as e:
            logger.error(f"Error getting surrounding data: {str(e)}")
            return []

    async def _insert_interpolated_record(
        self,
        missing_date: date,
        interpolated_value: Decimal,
        source_dates: List[date]
    ):
        """補間レコードを挿入"""
        try:
            exchange_rate = ExchangeRate(
                date=missing_date,
                open_rate=interpolated_value,
                high_rate=interpolated_value,
                low_rate=interpolated_value,
                close_rate=interpolated_value,
                volume=None,
                source=DataSourceType.YAHOO_FINANCE,  # デフォルトソース
                is_holiday=False,
                is_interpolated=True
            )
            
            self.db.add(exchange_rate)
            await self.db.commit()

        except Exception as e:
            logger.error(f"Error inserting interpolated record: {str(e)}")
            await self.db.rollback()
            raise

    async def _update_outlier_record(self, record_id: int, corrected_value: Decimal):
        """外れ値レコードを更新"""
        try:
            stmt = (
                update(ExchangeRate)
                .where(ExchangeRate.id == record_id)
                .values(
                    close_rate=corrected_value,
                    updated_at=datetime.now()
                )
            )
            
            await self.db.execute(stmt)
            await self.db.commit()

        except Exception as e:
            logger.error(f"Error updating outlier record: {str(e)}")
            await self.db.rollback()
            raise

    async def _select_best_duplicate_record(self, record_ids: List[int]) -> int:
        """最適な重複レコードを選択"""
        try:
            # 最新作成日時のレコードを選択
            stmt = (
                select(ExchangeRate.id)
                .where(ExchangeRate.id.in_(record_ids))
                .order_by(desc(ExchangeRate.created_at))
                .limit(1)
            )
            
            result = await self.db.execute(stmt)
            best_id = result.scalar()
            
            return best_id if best_id else record_ids[0]

        except Exception as e:
            logger.error(f"Error selecting best duplicate record: {str(e)}")
            return record_ids[0]

    async def _remove_duplicate_records(
        self, 
        record_ids: List[int], 
        keep_record_id: int
    ) -> int:
        """重複レコードを削除"""
        try:
            remove_ids = [rid for rid in record_ids if rid != keep_record_id]
            
            if not remove_ids:
                return 0
            
            delete_stmt = text(
                "DELETE FROM exchange_rates WHERE id = ANY(:ids)"
            )
            
            result = await self.db.execute(
                delete_stmt,
                {"ids": remove_ids}
            )
            
            await self.db.commit()
            return result.rowcount if hasattr(result, 'rowcount') else len(remove_ids)

        except Exception as e:
            logger.error(f"Error removing duplicate records: {str(e)}")
            await self.db.rollback()
            return 0

    async def _update_ohlc_record(self, record_id: int, corrected_ohlc: Dict[str, float]):
        """OHLC整合性を修正"""
        try:
            stmt = (
                update(ExchangeRate)
                .where(ExchangeRate.id == record_id)
                .values(
                    open_rate=Decimal(str(corrected_ohlc["open"])),
                    high_rate=Decimal(str(corrected_ohlc["high"])),
                    low_rate=Decimal(str(corrected_ohlc["low"])),
                    close_rate=Decimal(str(corrected_ohlc["close"])),
                    updated_at=datetime.now()
                )
            )
            
            await self.db.execute(stmt)
            await self.db.commit()

        except Exception as e:
            logger.error(f"Error updating OHLC record: {str(e)}")
            await self.db.rollback()
            raise

    def _correct_ohlc_consistency(self, ohlc_values: Dict[str, Any]) -> Dict[str, float]:
        """OHLC整合性を修正"""
        open_val = float(ohlc_values.get("open", 0))
        high_val = float(ohlc_values.get("high", 0))
        low_val = float(ohlc_values.get("low", 0))
        close_val = float(ohlc_values.get("close", 0))
        
        # closeを基準に他の値を調整
        corrected_high = max(high_val, open_val, close_val)
        corrected_low = min(low_val, open_val, close_val)
        
        return {
            "open": open_val,
            "high": corrected_high,
            "low": corrected_low,
            "close": close_val
        }

    def _create_error_response(
        self, 
        repair_id: str, 
        error_message: str
    ) -> DataRepairResponse:
        """エラーレスポンスを作成"""
        return DataRepairResponse(
            repair_id=repair_id,
            status="failed",
            is_dry_run=False,
            message=error_message,
            started_at=datetime.now(),
            estimated_completion=None,
            targets_count=0,
            total_date_range={"start": date.today(), "end": date.today()},
            repair_results=[],
            errors=[error_message],
            warnings=[],
            completed_at=datetime.now(),
            total_execution_time=0
        )