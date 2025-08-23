"""
Forex Prediction System - Data Quality Service
==============================================

データ品質レポートサービス（エンドポイント 4.3 用）
データ品質分析・監視・レポート生成機能を提供
"""

import logging
import uuid
from datetime import datetime, timedelta, date
from typing import Optional, List, Dict, Any
from decimal import Decimal
from sqlalchemy.orm import Session
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_, desc, text
import json

from ..models import (
    ExchangeRate, DataQuality, DataSource,
    DataSourceType, DataSourceStatus
)
from ..schemas.data import (
    DataQualityReport, DataQualityMetrics, QualityIssue,
    SourceQualityScore
)

logger = logging.getLogger(__name__)


class QualityService:
    """データ品質レポートサービスクラス"""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def generate_data_quality_report(
        self, 
        period_days: int = 7
    ) -> DataQualityReport:
        """
        データ品質レポートを生成
        
        Args:
            period_days: 分析期間（日数）
            
        Returns:
            DataQualityReport: 包括的な品質分析レポート
        """
        try:
            current_time = datetime.now()
            analysis_start = current_time - timedelta(days=period_days)
            report_id = f"quality_{uuid.uuid4().hex[:8]}"
            
            logger.info(f"Generating quality report: {report_id} for {period_days} days")
            
            # 分析期間の設定
            analysis_period = {
                "start": analysis_start.date(),
                "end": current_time.date()
            }
            
            # 全体品質指標を計算
            overall_metrics = await self._calculate_overall_quality_metrics(
                analysis_start.date(), current_time.date()
            )
            
            # ソース別品質スコアを計算
            source_scores = await self._calculate_source_quality_scores(
                analysis_start.date(), current_time.date()
            )
            
            # 品質問題を検出
            quality_issues = await self._detect_quality_issues(
                analysis_start.date(), current_time.date()
            )
            
            # 品質傾向を分析
            quality_trends = await self._analyze_quality_trends(
                analysis_start.date(), current_time.date()
            )
            
            # 全体品質スコアを計算
            overall_quality_score = self._calculate_overall_quality_score(
                overall_metrics, source_scores
            )
            
            # データヘルス状態を評価
            data_health_status = self._evaluate_data_health_status(
                overall_quality_score, quality_issues
            )
            
            # 推奨事項を生成
            recommendations = self._generate_quality_recommendations(
                overall_metrics, source_scores, quality_issues
            )
            
            return DataQualityReport(
                report_id=report_id,
                report_date=current_time,
                analysis_period=analysis_period,
                overall_quality_score=overall_quality_score,
                data_health_status=data_health_status,
                quality_metrics=overall_metrics,
                source_scores=source_scores,
                quality_issues=quality_issues,
                quality_trends=quality_trends,
                recommendations=recommendations,
                next_analysis_scheduled=current_time + timedelta(hours=24)
            )

        except Exception as e:
            logger.error(f"Error generating quality report: {str(e)}")
            return await self._create_fallback_quality_report()

    async def _calculate_overall_quality_metrics(
        self, 
        start_date: date, 
        end_date: date
    ) -> DataQualityMetrics:
        """全体品質指標を計算"""
        try:
            # 分析期間内の総レコード数
            total_records_stmt = (
                select(func.count(ExchangeRate.id))
                .where(
                    and_(
                        ExchangeRate.date >= start_date,
                        ExchangeRate.date <= end_date
                    )
                )
            )
            total_records = await self.db.execute(total_records_stmt)
            total_count = total_records.scalar() or 0
            
            if total_count == 0:
                return self._get_default_quality_metrics()
            
            # 完全性率の計算（close_rateがあるレコード）
            complete_records_stmt = (
                select(func.count(ExchangeRate.id))
                .where(
                    and_(
                        ExchangeRate.date >= start_date,
                        ExchangeRate.date <= end_date,
                        ExchangeRate.close_rate.isnot(None)
                    )
                )
            )
            complete_result = await self.db.execute(complete_records_stmt)
            complete_count = complete_result.scalar() or 0
            
            completeness_rate = complete_count / total_count
            
            # 補間データ件数
            interpolated_stmt = (
                select(func.count(ExchangeRate.id))
                .where(
                    and_(
                        ExchangeRate.date >= start_date,
                        ExchangeRate.date <= end_date,
                        ExchangeRate.is_interpolated == True
                    )
                )
            )
            interpolated_result = await self.db.execute(interpolated_stmt)
            interpolated_count = interpolated_result.scalar() or 0
            
            # 外れ値検出
            outlier_count = await self._detect_outliers_in_period(start_date, end_date)
            
            # 重複データチェック
            duplicate_count = await self._detect_duplicates_in_period(start_date, end_date)
            
            # 正確性率の計算（外れ値・重複を考慮）
            accuracy_issues = outlier_count + duplicate_count
            accuracy_rate = max(0, 1.0 - (accuracy_issues / total_count))
            
            # 整合性率の計算（補間データの割合を考慮）
            consistency_rate = max(0, 1.0 - (interpolated_count / total_count))
            
            # 総合品質スコア
            quality_score = (completeness_rate + accuracy_rate + consistency_rate) / 3
            
            return DataQualityMetrics(
                completeness_rate=completeness_rate,
                accuracy_rate=accuracy_rate,
                consistency_rate=consistency_rate,
                outlier_count=outlier_count,
                duplicate_count=duplicate_count,
                last_quality_check=datetime.now(),
                quality_score=quality_score
            )

        except Exception as e:
            logger.error(f"Error calculating quality metrics: {str(e)}")
            return self._get_default_quality_metrics()

    async def _calculate_source_quality_scores(
        self, 
        start_date: date, 
        end_date: date
    ) -> List[SourceQualityScore]:
        """ソース別品質スコアを計算"""
        try:
            source_scores = []
            
            # 各データソースタイプについて分析
            for source_type in [DataSourceType.YAHOO_FINANCE, DataSourceType.BOJ_CSV, DataSourceType.ALPHA_VANTAGE]:
                source_score = await self._calculate_single_source_quality(
                    source_type, start_date, end_date
                )
                if source_score:
                    source_scores.append(source_score)
            
            return source_scores

        except Exception as e:
            logger.error(f"Error calculating source quality scores: {str(e)}")
            return []

    async def _calculate_single_source_quality(
        self, 
        source_type: DataSourceType, 
        start_date: date, 
        end_date: date
    ) -> Optional[SourceQualityScore]:
        """単一ソースの品質スコアを計算"""
        try:
            # ソース別レコード数を取得
            source_records_stmt = (
                select(func.count(ExchangeRate.id))
                .where(
                    and_(
                        ExchangeRate.date >= start_date,
                        ExchangeRate.date <= end_date,
                        ExchangeRate.source == source_type
                    )
                )
            )
            source_result = await self.db.execute(source_records_stmt)
            source_count = source_result.scalar() or 0
            
            if source_count == 0:
                return None
            
            # 完全性スコア
            complete_source_stmt = (
                select(func.count(ExchangeRate.id))
                .where(
                    and_(
                        ExchangeRate.date >= start_date,
                        ExchangeRate.date <= end_date,
                        ExchangeRate.source == source_type,
                        ExchangeRate.close_rate.isnot(None)
                    )
                )
            )
            complete_source_result = await self.db.execute(complete_source_stmt)
            complete_source_count = complete_source_result.scalar() or 0
            
            completeness_score = complete_source_count / source_count
            
            # 正確性スコア（外れ値率から計算）
            source_outliers = await self._detect_source_outliers(
                source_type, start_date, end_date
            )
            accuracy_score = max(0, 1.0 - (source_outliers / source_count))
            
            # 適時性スコア（最新データの新鮮度）
            timeliness_score = await self._calculate_timeliness_score(
                source_type, end_date
            )
            
            # 総合スコア
            overall_score = (completeness_score + accuracy_score + timeliness_score) / 3
            
            # ソース名のマッピング
            source_names = {
                DataSourceType.YAHOO_FINANCE: "Yahoo Finance",
                DataSourceType.BOJ_CSV: "BOJ CSV Data",
                DataSourceType.ALPHA_VANTAGE: "Alpha Vantage"
            }
            
            return SourceQualityScore(
                source_name=source_names.get(source_type, source_type.value),
                source_type=source_type,
                completeness_score=completeness_score,
                accuracy_score=accuracy_score,
                timeliness_score=timeliness_score,
                overall_score=overall_score,
                data_points_analyzed=source_count,
                last_analysis=datetime.now()
            )

        except Exception as e:
            logger.error(f"Error calculating source quality for {source_type}: {str(e)}")
            return None

    async def _detect_outliers_in_period(
        self, 
        start_date: date, 
        end_date: date
    ) -> int:
        """期間内の外れ値を検出"""
        try:
            # レート値を取得
            rates_stmt = (
                select(ExchangeRate.close_rate)
                .where(
                    and_(
                        ExchangeRate.date >= start_date,
                        ExchangeRate.date <= end_date,
                        ExchangeRate.close_rate.isnot(None)
                    )
                )
            )
            rates_result = await self.db.execute(rates_stmt)
            rates = [float(rate) for rate in rates_result.scalars().all()]
            
            if len(rates) < 10:  # データが少なすぎる場合
                return 0
            
            # 統計的外れ値検出（3σ法）
            mean_rate = sum(rates) / len(rates)
            variance = sum((x - mean_rate) ** 2 for x in rates) / len(rates)
            std_dev = variance ** 0.5
            
            outlier_count = sum(
                1 for rate in rates 
                if abs(rate - mean_rate) > 3 * std_dev
            )
            
            return outlier_count

        except Exception as e:
            logger.error(f"Error detecting outliers: {str(e)}")
            return 0

    async def _detect_duplicates_in_period(
        self, 
        start_date: date, 
        end_date: date
    ) -> int:
        """期間内の重複データを検出"""
        try:
            # 同一日付・レートの重複を検出
            duplicates_stmt = text("""
                SELECT COUNT(*) - COUNT(DISTINCT date, close_rate)
                FROM exchange_rates
                WHERE date >= :start_date AND date <= :end_date
                AND close_rate IS NOT NULL
            """)
            
            duplicates_result = await self.db.execute(
                duplicates_stmt,
                {"start_date": start_date, "end_date": end_date}
            )
            return duplicates_result.scalar() or 0

        except Exception as e:
            logger.error(f"Error detecting duplicates: {str(e)}")
            return 0

    async def _detect_source_outliers(
        self, 
        source_type: DataSourceType, 
        start_date: date, 
        end_date: date
    ) -> int:
        """特定ソースの外れ値を検出"""
        try:
            rates_stmt = (
                select(ExchangeRate.close_rate)
                .where(
                    and_(
                        ExchangeRate.date >= start_date,
                        ExchangeRate.date <= end_date,
                        ExchangeRate.source == source_type,
                        ExchangeRate.close_rate.isnot(None)
                    )
                )
            )
            rates_result = await self.db.execute(rates_stmt)
            rates = [float(rate) for rate in rates_result.scalars().all()]
            
            if len(rates) < 5:
                return 0
            
            # 統計的外れ値検出
            mean_rate = sum(rates) / len(rates)
            variance = sum((x - mean_rate) ** 2 for x in rates) / len(rates)
            std_dev = variance ** 0.5
            
            outlier_count = sum(
                1 for rate in rates 
                if abs(rate - mean_rate) > 2.5 * std_dev  # ソース別は2.5σで判定
            )
            
            return outlier_count

        except Exception as e:
            logger.error(f"Error detecting source outliers: {str(e)}")
            return 0

    async def _calculate_timeliness_score(
        self, 
        source_type: DataSourceType, 
        end_date: date
    ) -> float:
        """適時性スコアを計算"""
        try:
            # 最新データの日付を取得
            latest_stmt = (
                select(ExchangeRate.date)
                .where(ExchangeRate.source == source_type)
                .order_by(desc(ExchangeRate.date))
                .limit(1)
            )
            latest_result = await self.db.execute(latest_stmt)
            latest_date = latest_result.scalar()
            
            if not latest_date:
                return 0.0
            
            # 最新性の評価（営業日ベース）
            days_behind = (end_date - latest_date).days
            
            if days_behind <= 1:
                return 1.0
            elif days_behind <= 3:
                return 0.8
            elif days_behind <= 7:
                return 0.6
            elif days_behind <= 14:
                return 0.4
            else:
                return 0.2

        except Exception as e:
            logger.error(f"Error calculating timeliness score: {str(e)}")
            return 0.5

    async def _detect_quality_issues(
        self, 
        start_date: date, 
        end_date: date
    ) -> List[QualityIssue]:
        """品質問題を検出"""
        try:
            issues = []
            
            # 欠損データの検出
            missing_issues = await self._detect_missing_data_issues(start_date, end_date)
            issues.extend(missing_issues)
            
            # 外れ値の検出
            outlier_issues = await self._detect_outlier_issues(start_date, end_date)
            issues.extend(outlier_issues)
            
            # データソース問題の検出
            source_issues = await self._detect_source_issues(start_date, end_date)
            issues.extend(source_issues)
            
            return issues

        except Exception as e:
            logger.error(f"Error detecting quality issues: {str(e)}")
            return []

    async def _detect_missing_data_issues(
        self, 
        start_date: date, 
        end_date: date
    ) -> List[QualityIssue]:
        """欠損データ問題を検出"""
        issues = []
        
        try:
            # 営業日で欠損している日付を検出
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
                    WHERE EXTRACT(DOW FROM date) NOT IN (0, 6)  -- 土日を除外
                ),
                missing_days AS (
                    SELECT bd.date
                    FROM business_days bd
                    LEFT JOIN exchange_rates er ON bd.date = er.date
                    WHERE er.date IS NULL
                )
                SELECT date FROM missing_days ORDER BY date
            """)
            
            missing_result = await self.db.execute(
                missing_dates_stmt,
                {"start_date": start_date, "end_date": end_date}
            )
            missing_dates = [row[0] for row in missing_result.fetchall()]
            
            if missing_dates:
                issues.append(QualityIssue(
                    issue_type="missing_data",
                    severity="medium" if len(missing_dates) < 5 else "high",
                    affected_dates=missing_dates[:10],  # 最大10件まで表示
                    affected_count=len(missing_dates),
                    description=f"{len(missing_dates)} business days missing exchange rate data",
                    suggested_action="Run data collection for missing dates or enable interpolation",
                    is_auto_repairable=True
                ))

        except Exception as e:
            logger.error(f"Error detecting missing data issues: {str(e)}")
        
        return issues

    async def _detect_outlier_issues(
        self, 
        start_date: date, 
        end_date: date
    ) -> List[QualityIssue]:
        """外れ値問題を検出"""
        issues = []
        
        try:
            # 統計的外れ値を持つ日付を特定
            outlier_dates_stmt = text("""
                WITH rate_stats AS (
                    SELECT 
                        AVG(close_rate::numeric) as mean_rate,
                        STDDEV(close_rate::numeric) as std_dev
                    FROM exchange_rates
                    WHERE date >= :start_date AND date <= :end_date
                    AND close_rate IS NOT NULL
                ),
                outliers AS (
                    SELECT er.date, er.close_rate
                    FROM exchange_rates er
                    CROSS JOIN rate_stats rs
                    WHERE er.date >= :start_date AND er.date <= :end_date
                    AND er.close_rate IS NOT NULL
                    AND ABS(er.close_rate::numeric - rs.mean_rate) > 3 * rs.std_dev
                )
                SELECT date FROM outliers ORDER BY date
            """)
            
            outlier_result = await self.db.execute(
                outlier_dates_stmt,
                {"start_date": start_date, "end_date": end_date}
            )
            outlier_dates = [row[0] for row in outlier_result.fetchall()]
            
            if outlier_dates:
                issues.append(QualityIssue(
                    issue_type="outlier_values",
                    severity="low" if len(outlier_dates) < 3 else "medium",
                    affected_dates=outlier_dates[:5],  # 最大5件まで表示
                    affected_count=len(outlier_dates),
                    description=f"{len(outlier_dates)} exchange rate values appear to be statistical outliers",
                    suggested_action="Verify outlier values against multiple data sources",
                    is_auto_repairable=False
                ))

        except Exception as e:
            logger.error(f"Error detecting outlier issues: {str(e)}")
        
        return issues

    async def _detect_source_issues(
        self, 
        start_date: date, 
        end_date: date
    ) -> List[QualityIssue]:
        """データソース問題を検出"""
        issues = []
        
        try:
            # エラー状態のデータソースを検出
            error_sources_stmt = (
                select(DataSource.name, DataSource.source_type)
                .where(DataSource.status == DataSourceStatus.ERROR)
            )
            error_result = await self.db.execute(error_sources_stmt)
            error_sources = error_result.fetchall()
            
            if error_sources:
                source_names = [row[0] for row in error_sources]
                issues.append(QualityIssue(
                    issue_type="source_unavailable",
                    severity="high",
                    affected_dates=[date.today()],
                    affected_count=len(error_sources),
                    description=f"Data sources in error state: {', '.join(source_names)}",
                    suggested_action="Check data source configurations and connectivity",
                    is_auto_repairable=False
                ))

        except Exception as e:
            logger.error(f"Error detecting source issues: {str(e)}")
        
        return issues

    async def _analyze_quality_trends(
        self, 
        start_date: date, 
        end_date: date
    ) -> Dict[str, float]:
        """品質傾向を分析（過去との比較）"""
        try:
            # 前期間の品質指標を取得
            previous_period_start = start_date - timedelta(days=(end_date - start_date).days)
            previous_period_end = start_date
            
            current_metrics = await self._calculate_overall_quality_metrics(
                start_date, end_date
            )
            previous_metrics = await self._calculate_overall_quality_metrics(
                previous_period_start, previous_period_end
            )
            
            return {
                "completeness_change": current_metrics.completeness_rate - previous_metrics.completeness_rate,
                "accuracy_change": current_metrics.accuracy_rate - previous_metrics.accuracy_rate,
                "consistency_change": current_metrics.consistency_rate - previous_metrics.consistency_rate,
                "overall_change": current_metrics.quality_score - previous_metrics.quality_score
            }

        except Exception as e:
            logger.error(f"Error analyzing quality trends: {str(e)}")
            return {
                "completeness_change": 0.0,
                "accuracy_change": 0.0,
                "consistency_change": 0.0,
                "overall_change": 0.0
            }

    def _calculate_overall_quality_score(
        self, 
        metrics: DataQualityMetrics, 
        source_scores: List[SourceQualityScore]
    ) -> float:
        """全体品質スコアを計算"""
        base_score = metrics.quality_score
        
        # ソーススコアによる重み付け調整
        if source_scores:
            source_avg = sum(score.overall_score for score in source_scores) / len(source_scores)
            # ベーススコアとソース平均の加重平均
            overall_score = (base_score * 0.7) + (source_avg * 0.3)
        else:
            overall_score = base_score
        
        return min(1.0, max(0.0, overall_score))

    def _evaluate_data_health_status(
        self, 
        overall_score: float, 
        issues: List[QualityIssue]
    ) -> str:
        """データヘルス状態を評価"""
        critical_issues = sum(1 for issue in issues if issue.severity == "critical")
        high_issues = sum(1 for issue in issues if issue.severity == "high")
        
        if critical_issues > 0 or overall_score < 0.7:
            return "poor"
        elif high_issues > 2 or overall_score < 0.85:
            return "fair"
        elif overall_score < 0.95:
            return "good"
        else:
            return "excellent"

    def _generate_quality_recommendations(
        self,
        metrics: DataQualityMetrics,
        source_scores: List[SourceQualityScore],
        issues: List[QualityIssue]
    ) -> List[str]:
        """品質改善推奨事項を生成"""
        recommendations = []
        
        # 完全性に関する推奨
        if metrics.completeness_rate < 0.95:
            recommendations.append(
                "データ完全性が95%を下回っています。自動収集の頻度を増やすか、"
                "バックアップデータソースの追加を検討してください。"
            )
        
        # 正確性に関する推奨
        if metrics.accuracy_rate < 0.98:
            recommendations.append(
                "データ正確性に問題があります。外れ値検出アルゴリズムの調整と"
                "複数ソースでのデータ検証を実施してください。"
            )
        
        # ソース固有の推奨
        poor_sources = [s for s in source_scores if s.overall_score < 0.8]
        if poor_sources:
            source_names = [s.source_name for s in poor_sources]
            recommendations.append(
                f"品質スコアが低いデータソース（{', '.join(source_names)}）の"
                "設定見直しまたは代替ソースの検討を推奨します。"
            )
        
        # 問題ベースの推奨
        if any(issue.issue_type == "missing_data" for issue in issues):
            recommendations.append(
                "欠損データが検出されました。データ収集スケジュールの見直しと"
                "補間機能の活用を検討してください。"
            )
        
        return recommendations

    def _get_default_quality_metrics(self) -> DataQualityMetrics:
        """デフォルト品質指標"""
        return DataQualityMetrics(
            completeness_rate=0.950,
            accuracy_rate=0.995,
            consistency_rate=0.985,
            outlier_count=0,
            duplicate_count=0,
            last_quality_check=datetime.now(),
            quality_score=0.977
        )

    async def _create_fallback_quality_report(self) -> DataQualityReport:
        """フォールバック品質レポート"""
        current_time = datetime.now()
        
        return DataQualityReport(
            report_id=f"fallback_{uuid.uuid4().hex[:8]}",
            report_date=current_time,
            analysis_period={
                "start": (current_time - timedelta(days=7)).date(),
                "end": current_time.date()
            },
            overall_quality_score=0.950,
            data_health_status="good",
            quality_metrics=self._get_default_quality_metrics(),
            source_scores=[],
            quality_issues=[],
            quality_trends={
                "completeness_change": 0.0,
                "accuracy_change": 0.0,
                "consistency_change": 0.0,
                "overall_change": 0.0
            },
            recommendations=[
                "品質分析サービスが一時的に利用できません。",
                "システム管理者に連絡してください。"
            ],
            next_analysis_scheduled=current_time + timedelta(hours=1)
        )