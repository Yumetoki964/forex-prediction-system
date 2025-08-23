"""
Forex Prediction System - Alerts Service
========================================

アラート関連のビジネスロジック実装
アクティブアラートの管理とアラート生成機能
"""

from datetime import datetime, date, timedelta
from decimal import Decimal
from typing import Optional, List, Dict, Any
import json
import logging
from sqlalchemy import select, desc, and_, func, or_
from sqlalchemy.ext.asyncio import AsyncSession

from ..models import (
    ActiveAlert, AlertSetting, AlertType, ExchangeRate, 
    Prediction, TradingSignal, SignalType
)
from ..schemas.alerts import (
    ActiveAlertResponse, ActiveAlertsResponse,
    AlertAcknowledgeRequest, AlertSeverityInfo
)

logger = logging.getLogger(__name__)


class AlertsService:
    """アラートサービス"""
    
    def __init__(self, db: AsyncSession):
        self.db = db
    
    # ===================================================================
    # 基本CRUD操作
    # ===================================================================
    
    async def get_all(self, skip: int = 0, limit: int = 100) -> List[ActiveAlertResponse]:
        """全アクティブアラートを取得"""
        stmt = (
            select(ActiveAlert)
            .order_by(desc(ActiveAlert.created_at))
            .offset(skip)
            .limit(limit)
        )
        result = await self.db.execute(stmt)
        alerts = result.scalars().all()
        
        # UI表示用情報を追加してレスポンス作成
        responses = []
        for alert in alerts:
            response = await self._create_alert_response(alert)
            responses.append(response)
        
        return responses
    
    async def get_by_id(self, alert_id: int) -> Optional[ActiveAlertResponse]:
        """IDでアクティブアラートを取得"""
        stmt = select(ActiveAlert).where(ActiveAlert.id == alert_id)
        result = await self.db.execute(stmt)
        alert = result.scalar_one_or_none()
        
        if alert:
            return await self._create_alert_response(alert)
        return None
    
    # ===================================================================
    # ビジネスロジック実装
    # ===================================================================
    
    async def get_active_alerts(self) -> ActiveAlertsResponse:
        """
        アクティブアラート一覧を取得
        
        自動的にアラート生成・更新を実行してから最新状態を返す
        UI表示用のサマリー情報も含む
        """
        # アラート自動生成・更新を実行
        await self._auto_generate_alerts()
        
        # アクティブアラートを取得（優先度順）
        alerts = await self._get_prioritized_alerts()
        
        # サマリー情報を計算
        summary = await self._calculate_alert_summary(alerts)
        
        return ActiveAlertsResponse(
            alerts=alerts,
            **summary
        )
    
    async def acknowledge_alerts(self, request: AlertAcknowledgeRequest) -> Dict[str, Any]:
        """アラートを確認済みにする"""
        acknowledged_count = 0
        acknowledged_at = datetime.now()
        
        for alert_id in request.alert_ids:
            stmt = select(ActiveAlert).where(ActiveAlert.id == alert_id)
            result = await self.db.execute(stmt)
            alert = result.scalar_one_or_none()
            
            if alert and not alert.is_acknowledged:
                alert.is_acknowledged = True
                alert.acknowledged_at = acknowledged_at
                acknowledged_count += 1
        
        if acknowledged_count > 0:
            await self.db.commit()
            logger.info(f"{acknowledged_count}件のアラートを確認済みにしました")
        
        return {
            "message": f"{acknowledged_count}件のアラートを確認済みにしました",
            "acknowledged_ids": request.alert_ids,
            "acknowledged_at": acknowledged_at,
            "acknowledged_count": acknowledged_count
        }
    
    async def _get_prioritized_alerts(self) -> List[ActiveAlertResponse]:
        """優先度順にアラートを取得"""
        # 未確認・重要度・時刻順でソート
        stmt = (
            select(ActiveAlert)
            .order_by(
                ActiveAlert.is_acknowledged.asc(),  # 未確認を先に
                desc(
                    func.case(
                        (ActiveAlert.severity == 'critical', 4),
                        (ActiveAlert.severity == 'high', 3),
                        (ActiveAlert.severity == 'medium', 2),
                        else_=1
                    )
                ),  # 重要度順
                desc(ActiveAlert.created_at)  # 新しい順
            )
            .limit(50)  # 最大50件
        )
        result = await self.db.execute(stmt)
        alerts = result.scalars().all()
        
        responses = []
        for alert in alerts:
            response = await self._create_alert_response(alert)
            responses.append(response)
        
        return responses
    
    async def _calculate_alert_summary(
        self, 
        alerts: List[ActiveAlertResponse]
    ) -> Dict[str, Any]:
        """アラートサマリー情報を計算"""
        total_alerts = len(alerts)
        unacknowledged_alerts = [a for a in alerts if not a.is_acknowledged]
        unacknowledged_count = len(unacknowledged_alerts)
        critical_count = len([a for a in alerts if a.severity == "critical"])
        
        # 重要度別カウント
        counts_by_severity = {}
        for alert in alerts:
            severity = alert.severity
            counts_by_severity[severity] = counts_by_severity.get(severity, 0) + 1
        
        # 最新アラート時刻
        latest_alert_at = max(
            [alert.created_at for alert in alerts]
        ) if alerts else None
        
        # UI制御フラグ
        show_notification_badge = unacknowledged_count > 0
        requires_attention = critical_count > 0 or unacknowledged_count >= 3
        
        return {
            "total_alerts": total_alerts,
            "unacknowledged_count": unacknowledged_count,
            "critical_count": critical_count,
            "counts_by_severity": counts_by_severity,
            "latest_alert_at": latest_alert_at,
            "show_notification_badge": show_notification_badge,
            "requires_attention": requires_attention,
            "last_updated": datetime.now()
        }
    
    # ===================================================================
    # 自動アラート生成
    # ===================================================================
    
    async def _auto_generate_alerts(self) -> None:
        """自動アラート生成・更新を実行"""
        try:
            # 1. レート急変動アラートをチェック
            await self._check_rate_volatility_alerts()
            
            # 2. シグナル変更アラートをチェック
            await self._check_signal_change_alerts()
            
            # 3. 予測信頼度低下アラートをチェック
            await self._check_prediction_confidence_alerts()
            
            # 4. データ品質アラートをチェック
            await self._check_data_quality_alerts()
            
            # 5. 古いアラートをクリーンアップ
            await self._cleanup_old_alerts()
            
        except Exception as e:
            logger.error(f"自動アラート生成でエラーが発生: {e}")
    
    async def _check_rate_volatility_alerts(self) -> None:
        """レート急変動アラートをチェック"""
        # 過去24時間のレート変動を確認
        yesterday = date.today() - timedelta(days=1)
        
        # 昨日と今日のレートを取得
        stmt_yesterday = (
            select(ExchangeRate)
            .where(ExchangeRate.date == yesterday)
            .limit(1)
        )
        stmt_today = (
            select(ExchangeRate)
            .order_by(desc(ExchangeRate.date))
            .limit(1)
        )
        
        result_yesterday = await self.db.execute(stmt_yesterday)
        result_today = await self.db.execute(stmt_today)
        
        yesterday_rate = result_yesterday.scalar_one_or_none()
        today_rate = result_today.scalar_one_or_none()
        
        if not yesterday_rate or not today_rate:
            return
        
        # 変動率を計算
        change_rate = (
            (float(today_rate.close_rate) - float(yesterday_rate.close_rate)) / 
            float(yesterday_rate.close_rate)
        ) * 100
        
        # 1.5%以上の変動でアラート
        if abs(change_rate) >= 1.5:
            # 既存のアラートをチェック（重複防止）
            existing_alert = await self._check_existing_alert(
                alert_type="rate_threshold",
                reference_date=date.today()
            )
            
            if not existing_alert:
                severity = "high" if abs(change_rate) >= 2.5 else "medium"
                direction = "上昇" if change_rate > 0 else "下落"
                
                await self._create_alert(
                    title="レート急変動アラート",
                    message=f"ドル円レートが24時間で{abs(change_rate):.1f}%{direction}しました。現在レート: {today_rate.close_rate}円",
                    severity=severity,
                    alert_setting_id=1,  # デフォルト設定
                    exchange_rate_id=today_rate.id,
                    icon="trending_up" if change_rate > 0 else "trending_down"
                )
    
    async def _check_signal_change_alerts(self) -> None:
        """シグナル変更アラートをチェック"""
        # 最新2つのシグナルを取得
        stmt = (
            select(TradingSignal)
            .order_by(desc(TradingSignal.date))
            .limit(2)
        )
        result = await self.db.execute(stmt)
        signals = result.scalars().all()
        
        if len(signals) < 2:
            return
        
        latest_signal, previous_signal = signals[0], signals[1]
        
        # シグナルが変更された場合
        if latest_signal.signal_type != previous_signal.signal_type:
            existing_alert = await self._check_existing_alert(
                alert_type="signal_change",
                reference_date=latest_signal.date
            )
            
            if not existing_alert:
                signal_text = self._get_signal_display_text(latest_signal.signal_type)
                
                await self._create_alert(
                    title="売買シグナル変更",
                    message=f"売買シグナルが'{signal_text}'に変更されました。信頼度: {latest_signal.confidence:.0%}",
                    severity="medium",
                    alert_setting_id=2,  # シグナル変更設定
                    prediction_id=latest_signal.prediction_id,
                    icon="swap_horiz"
                )
    
    async def _check_prediction_confidence_alerts(self) -> None:
        """予測信頼度低下アラートをチェック"""
        # 最新の1週間予測を取得
        stmt = (
            select(Prediction)
            .order_by(desc(Prediction.prediction_date))
            .limit(1)
        )
        result = await self.db.execute(stmt)
        prediction = result.scalar_one_or_none()
        
        if not prediction:
            return
        
        # 信頼度が70%を下回った場合
        if prediction.prediction_strength < 0.7:
            existing_alert = await self._check_existing_alert(
                alert_type="prediction_confidence_low",
                reference_date=prediction.prediction_date
            )
            
            if not existing_alert:
                await self._create_alert(
                    title="予測信頼度低下",
                    message=f"予測信頼度が{prediction.prediction_strength:.0%}に低下しました。市場の不確実性が高まっています。",
                    severity="medium",
                    alert_setting_id=3,  # 信頼度設定
                    prediction_id=prediction.id,
                    icon="warning"
                )
    
    async def _check_data_quality_alerts(self) -> None:
        """データ品質アラートをチェック"""
        # 最新のデータ更新時刻をチェック
        stmt = (
            select(ExchangeRate)
            .order_by(desc(ExchangeRate.created_at))
            .limit(1)
        )
        result = await self.db.execute(stmt)
        latest_rate = result.scalar_one_or_none()
        
        if not latest_rate:
            return
        
        # 24時間以上データが更新されていない場合
        hours_since_update = (
            datetime.now() - latest_rate.created_at
        ).total_seconds() / 3600
        
        if hours_since_update > 24:
            existing_alert = await self._check_existing_alert(
                alert_type="data_quality",
                reference_date=date.today()
            )
            
            if not existing_alert:
                await self._create_alert(
                    title="データ更新遅延",
                    message=f"為替データの更新が{hours_since_update:.1f}時間遅延しています。データソースを確認してください。",
                    severity="high",
                    alert_setting_id=4,  # データ品質設定
                    icon="sync_problem"
                )
    
    async def _check_existing_alert(
        self, 
        alert_type: str, 
        reference_date: date
    ) -> Optional[ActiveAlert]:
        """既存のアラートをチェック（重複防止）"""
        # 同日同種のアラートがあるかチェック
        stmt = (
            select(ActiveAlert)
            .where(
                and_(
                    ActiveAlert.title.contains(alert_type.replace("_", " ")),
                    func.date(ActiveAlert.created_at) == reference_date
                )
            )
            .limit(1)
        )
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()
    
    async def _create_alert(
        self,
        title: str,
        message: str,
        severity: str,
        alert_setting_id: int,
        exchange_rate_id: Optional[int] = None,
        prediction_id: Optional[int] = None,
        icon: str = "notification_important"
    ) -> ActiveAlert:
        """アラートを作成"""
        # 重要度に応じてカラーと緊急度を設定
        severity_info = AlertSeverityInfo.get_severity_info(severity)
        
        alert = ActiveAlert(
            alert_setting_id=alert_setting_id,
            title=title,
            message=message,
            severity=severity,
            exchange_rate_id=exchange_rate_id,
            prediction_id=prediction_id,
            is_acknowledged=False
        )
        
        self.db.add(alert)
        await self.db.commit()
        await self.db.refresh(alert)
        
        logger.info(f"アラートを作成しました: {title}")
        return alert
    
    async def _cleanup_old_alerts(self) -> None:
        """古いアラートをクリーンアップ"""
        # 30日以前の確認済みアラートを削除
        cutoff_date = datetime.now() - timedelta(days=30)
        
        stmt = (
            select(ActiveAlert)
            .where(
                and_(
                    ActiveAlert.is_acknowledged == True,
                    ActiveAlert.created_at < cutoff_date
                )
            )
        )
        result = await self.db.execute(stmt)
        old_alerts = result.scalars().all()
        
        if old_alerts:
            for alert in old_alerts:
                await self.db.delete(alert)
            
            await self.db.commit()
            logger.info(f"{len(old_alerts)}件の古いアラートを削除しました")
    
    # ===================================================================
    # ヘルパーメソッド
    # ===================================================================
    
    async def _create_alert_response(self, alert: ActiveAlert) -> ActiveAlertResponse:
        """ActiveAlertからActiveAlertResponseを作成"""
        severity_info = AlertSeverityInfo.get_severity_info(alert.severity)
        
        return ActiveAlertResponse(
            id=alert.id,
            alert_setting_id=alert.alert_setting_id,
            title=alert.title,
            message=alert.message,
            severity=alert.severity,
            is_acknowledged=alert.is_acknowledged,
            acknowledged_at=alert.acknowledged_at,
            exchange_rate_id=alert.exchange_rate_id,
            prediction_id=alert.prediction_id,
            icon=severity_info.icon,
            color_code=severity_info.color,
            urgency_level=severity_info.urgency,
            created_at=alert.created_at
        )
    
    def _get_signal_display_text(self, signal_type: SignalType) -> str:
        """シグナル表示テキストを生成"""
        display_map = {
            SignalType.STRONG_SELL: "強い売りシグナル",
            SignalType.SELL: "売りシグナル",
            SignalType.HOLD: "様子見",
            SignalType.BUY: "買いシグナル",
            SignalType.STRONG_BUY: "強い買いシグナル"
        }
        return display_map.get(signal_type, "不明")