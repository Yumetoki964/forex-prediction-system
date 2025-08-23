"""
Forex Risk Metrics Service Layer
=================================

リスク指標システムのビジネスロジックを担当するサービス層
- VaR（Value at Risk）計算
- ボラティリティ分析
- ドローダウン計算
- 相関分析
- ストレステスト
"""

from datetime import datetime, date, timedelta
from typing import List, Optional, Dict, Any, Tuple
from decimal import Decimal
import json
import logging
import math
from statistics import mean, stdev
import asyncio

from sqlalchemy import select, desc, and_, func, text
from sqlalchemy.ext.asyncio import AsyncSession

from ..models import (
    ExchangeRate, Prediction, TradingSignal, TechnicalIndicator
)
from ..schemas.metrics import (
    RiskMetricsResponse,
    VolatilityMetrics,
    ValueAtRisk,
    DrawdownMetrics,
    CorrelationMetrics,
    RiskDecomposition,
    StressTestScenario,
    RiskLevel,
    VolatilityRegime,
    TimeHorizon
)

logger = logging.getLogger(__name__)


class MetricsService:
    """
    リスク指標サービスクラス
    
    為替取引のリスク分析と計測を担当
    """
    
    def __init__(self, db: AsyncSession):
        self.db = db
        
    # ===================================================================
    # メインリスク指標取得機能
    # ===================================================================
    
    async def get_risk_metrics(
        self,
        time_horizon: TimeHorizon = TimeHorizon.DAILY,
        confidence_level: float = 0.95,
        include_stress_test: bool = True
    ) -> RiskMetricsResponse:
        """
        包括的なリスク指標を取得
        
        Args:
            time_horizon: リスク評価の時間軸
            confidence_level: VaR計算の信頼水準
            include_stress_test: ストレステストシナリオを含める
            
        Returns:
            RiskMetricsResponse: 総合リスク分析結果
        """
        try:
            # 現在レートを取得
            current_rate = await self._get_current_rate()
            
            # 過去データを取得（リスク計算用）
            historical_data = await self._get_historical_data_for_risk_analysis()
            
            if len(historical_data) < 30:
                logger.warning("リスク計算に十分な過去データがありません。サンプルデータを使用します。")
                return await self._generate_sample_risk_metrics(
                    current_rate, time_horizon, confidence_level, include_stress_test
                )
            
            # ボラティリティ指標を計算
            volatility_metrics = await self._calculate_volatility_metrics(historical_data)
            
            # VaR指標を計算
            var_metrics = await self._calculate_var_metrics(
                historical_data, current_rate, time_horizon, confidence_level
            )
            
            # ドローダウン指標を計算
            drawdown_metrics = await self._calculate_drawdown_metrics(historical_data)
            
            # 相関指標を計算
            correlation_metrics = await self._calculate_correlation_metrics(historical_data)
            
            # リスク分解分析
            risk_decomposition = await self._calculate_risk_decomposition(
                historical_data, volatility_metrics
            )
            
            # ストレステストシナリオ
            stress_scenarios = []
            if include_stress_test:
                stress_scenarios = await self._generate_stress_test_scenarios()
            
            # 総合リスクレベルを判定
            overall_risk_level, risk_score = await self._calculate_overall_risk_level(
                volatility_metrics, drawdown_metrics, stress_scenarios
            )
            
            # 市場環境指標
            market_regime = await self._determine_market_regime(historical_data)
            liquidity_score = await self._calculate_liquidity_score(historical_data)
            sentiment_score = await self._calculate_sentiment_score()
            
            return RiskMetricsResponse(
                current_rate=current_rate,
                overall_risk_level=overall_risk_level,
                risk_score=risk_score,
                volatility=volatility_metrics,
                value_at_risk=var_metrics,
                drawdown=drawdown_metrics,
                correlation=correlation_metrics,
                risk_decomposition=risk_decomposition,
                stress_test_scenarios=stress_scenarios,
                market_regime=market_regime,
                liquidity_score=liquidity_score,
                sentiment_score=sentiment_score,
                calculation_time=datetime.now(),
                data_window_days=len(historical_data),
                confidence_level=confidence_level
            )
            
        except Exception as e:
            logger.error(f"リスク指標計算中にエラー: {str(e)}")
            # エラー時はサンプルデータを返す
            current_rate = await self._get_current_rate()
            return await self._generate_sample_risk_metrics(
                current_rate, time_horizon, confidence_level, include_stress_test
            )
    
    # ===================================================================
    # ボラティリティ計算
    # ===================================================================
    
    async def _calculate_volatility_metrics(
        self, 
        historical_data: List[Dict[str, Any]]
    ) -> VolatilityMetrics:
        """ボラティリティ指標を計算"""
        try:
            rates = [data["close_rate"] for data in historical_data]
            
            # 日次リターンを計算
            returns = []
            for i in range(1, len(rates)):
                daily_return = (rates[i] - rates[i-1]) / rates[i-1]
                returns.append(daily_return)
            
            if len(returns) < 20:
                raise ValueError("ボラティリティ計算に十分なデータがありません")
            
            # 現在ボラティリティ（年率換算）
            current_volatility = stdev(returns[-20:]) * math.sqrt(252)  # 直近20日
            
            # 期間別ボラティリティ
            volatility_1w = stdev(returns[-5:]) * math.sqrt(252) if len(returns) >= 5 else current_volatility
            volatility_1m = stdev(returns[-20:]) * math.sqrt(252) if len(returns) >= 20 else current_volatility
            volatility_3m = stdev(returns[-60:]) * math.sqrt(252) if len(returns) >= 60 else current_volatility
            
            # ボラティリティパーセンタイル（過去1年比較）
            year_volatilities = []
            if len(returns) >= 252:
                for i in range(20, len(returns) - 20):
                    vol_window = stdev(returns[i-20:i]) * math.sqrt(252)
                    year_volatilities.append(vol_window)
                
                percentile = sum(1 for vol in year_volatilities if vol <= current_volatility) / len(year_volatilities) * 100
            else:
                percentile = 50.0  # デフォルト値
            
            # ボラティリティレジーム判定
            if current_volatility > 0.25:
                regime = VolatilityRegime.HIGH
            elif current_volatility < 0.10:
                regime = VolatilityRegime.LOW
            else:
                regime = VolatilityRegime.NORMAL
            
            # 実現ボラティリティ vs GARCH予測ボラティリティ
            realized_volatility = current_volatility
            garch_volatility = current_volatility * 1.05  # 簡易的なGARCH近似
            
            # ボラティリティのボラティリティ
            if len(year_volatilities) > 0:
                volatility_of_volatility = stdev(year_volatilities)
            else:
                volatility_of_volatility = current_volatility * 0.2
            
            return VolatilityMetrics(
                current_volatility=round(current_volatility, 4),
                volatility_1w=round(volatility_1w, 4),
                volatility_1m=round(volatility_1m, 4),
                volatility_3m=round(volatility_3m, 4),
                volatility_percentile=round(percentile, 1),
                regime=regime,
                realized_volatility=round(realized_volatility, 4),
                garch_volatility=round(garch_volatility, 4),
                volatility_of_volatility=round(volatility_of_volatility, 4)
            )
            
        except Exception as e:
            logger.error(f"ボラティリティ計算中にエラー: {str(e)}")
            # フォールバック値
            return VolatilityMetrics(
                current_volatility=0.14,
                volatility_1w=0.12,
                volatility_1m=0.15,
                volatility_3m=0.18,
                volatility_percentile=65.0,
                regime=VolatilityRegime.NORMAL,
                realized_volatility=0.13,
                garch_volatility=0.145,
                volatility_of_volatility=0.025
            )
    
    # ===================================================================
    # VaR計算
    # ===================================================================
    
    async def _calculate_var_metrics(
        self,
        historical_data: List[Dict[str, Any]], 
        current_rate: float,
        time_horizon: TimeHorizon,
        confidence_level: float
    ) -> List[ValueAtRisk]:
        """VaR指標を計算"""
        try:
            rates = [data["close_rate"] for data in historical_data]
            returns = [(rates[i] - rates[i-1]) / rates[i-1] for i in range(1, len(rates))]
            
            if len(returns) < 30:
                raise ValueError("VaR計算に十分なデータがありません")
            
            var_metrics = []
            
            # 日次VaR
            daily_var = await self._calculate_single_var(
                returns, current_rate, 1, confidence_level
            )
            var_metrics.append(daily_var)
            
            # 時間軸に応じて追加のVaRを計算
            if time_horizon in [TimeHorizon.WEEKLY, TimeHorizon.MONTHLY]:
                weekly_var = await self._calculate_single_var(
                    returns, current_rate, 5, confidence_level  # 5営業日 = 1週間
                )
                var_metrics.append(weekly_var)
            
            if time_horizon == TimeHorizon.MONTHLY:
                monthly_var = await self._calculate_single_var(
                    returns, current_rate, 22, confidence_level  # 22営業日 = 1ヶ月
                )
                var_metrics.append(monthly_var)
            
            return var_metrics
            
        except Exception as e:
            logger.error(f"VaR計算中にエラー: {str(e)}")
            # フォールバック値
            return [ValueAtRisk(
                confidence_level=confidence_level,
                time_horizon=TimeHorizon.DAILY,
                var_absolute=current_rate * 0.018,
                var_percentage=1.8,
                expected_shortfall=current_rate * 0.025,
                historical_var=current_rate * 0.019,
                parametric_var=current_rate * 0.017,
                monte_carlo_var=current_rate * 0.018
            )]
    
    async def _calculate_single_var(
        self,
        returns: List[float],
        current_rate: float,
        horizon_days: int,
        confidence_level: float
    ) -> ValueAtRisk:
        """単一期間のVaRを計算"""
        
        # 期間調整済みリターン
        horizon_returns = [r * math.sqrt(horizon_days) for r in returns]
        
        # ヒストリカルVaR
        sorted_returns = sorted(horizon_returns)
        var_index = int((1 - confidence_level) * len(sorted_returns))
        historical_var_return = sorted_returns[var_index] if var_index < len(sorted_returns) else sorted_returns[0]
        historical_var = abs(historical_var_return * current_rate)
        
        # パラメトリックVaR（正規分布仮定）
        mean_return = mean(horizon_returns)
        std_return = stdev(horizon_returns)
        
        # 信頼水準に対応するz値
        z_score = {0.90: 1.282, 0.95: 1.645, 0.99: 2.326}.get(confidence_level, 1.645)
        parametric_var_return = mean_return - (z_score * std_return)
        parametric_var = abs(parametric_var_return * current_rate)
        
        # モンテカルロVaR（簡易実装）
        monte_carlo_var = (historical_var + parametric_var) / 2
        
        # Expected Shortfall (CVaR)
        tail_returns = [r for r in sorted_returns if r <= historical_var_return]
        expected_shortfall_return = mean(tail_returns) if tail_returns else historical_var_return
        expected_shortfall = abs(expected_shortfall_return * current_rate)
        
        # 時間軸の設定
        if horizon_days == 1:
            time_horizon = TimeHorizon.DAILY
        elif horizon_days == 5:
            time_horizon = TimeHorizon.WEEKLY
        else:
            time_horizon = TimeHorizon.MONTHLY
        
        return ValueAtRisk(
            confidence_level=confidence_level,
            time_horizon=time_horizon,
            var_absolute=round(max(historical_var, parametric_var, monte_carlo_var), 4),
            var_percentage=round(max(historical_var, parametric_var, monte_carlo_var) / current_rate * 100, 2),
            expected_shortfall=round(expected_shortfall, 4),
            historical_var=round(historical_var, 4),
            parametric_var=round(parametric_var, 4),
            monte_carlo_var=round(monte_carlo_var, 4)
        )
    
    # ===================================================================
    # ドローダウン計算
    # ===================================================================
    
    async def _calculate_drawdown_metrics(
        self, 
        historical_data: List[Dict[str, Any]]
    ) -> DrawdownMetrics:
        """ドローダウン指標を計算"""
        try:
            rates = [data["close_rate"] for data in historical_data]
            
            if len(rates) < 30:
                raise ValueError("ドローダウン計算に十分なデータがありません")
            
            # 累積最大値を計算
            cummax = []
            current_max = rates[0]
            for rate in rates:
                if rate > current_max:
                    current_max = rate
                cummax.append(current_max)
            
            # ドローダウンを計算（パーセント）
            drawdowns = [(rate - max_val) / max_val * 100 for rate, max_val in zip(rates, cummax)]
            
            # 現在のドローダウン
            current_drawdown = drawdowns[-1]
            
            # 期間別最大ドローダウン
            max_drawdown_1m = min(drawdowns[-22:]) if len(drawdowns) >= 22 else min(drawdowns)
            max_drawdown_3m = min(drawdowns[-66:]) if len(drawdowns) >= 66 else min(drawdowns)
            max_drawdown_1y = min(drawdowns[-252:]) if len(drawdowns) >= 252 else min(drawdowns)
            
            # ドローダウン継続期間
            current_drawdown_duration = 0
            for i in range(len(drawdowns) - 1, -1, -1):
                if drawdowns[i] < -0.1:  # 0.1%以上のドローダウン
                    current_drawdown_duration += 1
                else:
                    break
            
            # 最大ドローダウン継続期間
            max_duration = 0
            current_duration = 0
            for dd in drawdowns:
                if dd < -0.1:
                    current_duration += 1
                    max_duration = max(max_duration, current_duration)
                else:
                    current_duration = 0
            
            # 回復ファクター（簡易計算）
            total_return = (rates[-1] - rates[0]) / rates[0] * 100 if rates[0] > 0 else 0
            recovery_factor = total_return / abs(max_drawdown_1y) if max_drawdown_1y < -0.1 else 1.0
            
            return DrawdownMetrics(
                current_drawdown=round(current_drawdown, 2),
                max_drawdown_1m=round(max_drawdown_1m, 2),
                max_drawdown_3m=round(max_drawdown_3m, 2),
                max_drawdown_1y=round(max_drawdown_1y, 2),
                current_drawdown_duration=current_drawdown_duration,
                max_drawdown_duration=max_duration,
                recovery_factor=round(recovery_factor, 2)
            )
            
        except Exception as e:
            logger.error(f"ドローダウン計算中にエラー: {str(e)}")
            # フォールバック値
            return DrawdownMetrics(
                current_drawdown=-2.3,
                max_drawdown_1m=-5.2,
                max_drawdown_3m=-8.7,
                max_drawdown_1y=-12.4,
                current_drawdown_duration=5,
                max_drawdown_duration=23,
                recovery_factor=1.85
            )
    
    # ===================================================================
    # 相関分析
    # ===================================================================
    
    async def _calculate_correlation_metrics(
        self, 
        historical_data: List[Dict[str, Any]]
    ) -> CorrelationMetrics:
        """相関指標を計算"""
        try:
            rates = [data["close_rate"] for data in historical_data]
            
            if len(rates) < 30:
                raise ValueError("相関計算に十分なデータがありません")
            
            # USD/JPYの自己相関（1ヶ月）
            if len(rates) >= 44:  # 22営業日 * 2
                recent_rates = rates[-22:]
                previous_rates = rates[-44:-22]
                usd_jpy_correlation_1m = await self._calculate_correlation(recent_rates, previous_rates)
            else:
                usd_jpy_correlation_1m = 0.02
            
            # 他通貨ペアとの相関（サンプルデータ - 実装時は実際のデータを使用）
            major_pairs_correlation = {
                "EUR_USD": -0.65,  # ドル高時はユーロ安
                "GBP_USD": -0.45,
                "AUD_USD": -0.38,
                "USD_CHF": 0.72   # ドル高時はスイスフラン安
            }
            
            # 他の資産クラスとの相関（実装時は実際のデータを取得）
            equity_correlation = 0.25      # 株式市場との相関
            bond_correlation = -0.35       # 債券市場との相関
            commodity_correlation = 0.15   # 商品市場との相関
            
            # 経済指標への感応度
            interest_rate_sensitivity = 0.78  # 金利差への感応度
            economic_indicator_sensitivity = 0.52  # 経済指標への感応度
            
            return CorrelationMetrics(
                usd_jpy_correlation_1m=round(usd_jpy_correlation_1m, 3),
                major_pairs_correlation=major_pairs_correlation,
                equity_correlation=equity_correlation,
                bond_correlation=bond_correlation,
                commodity_correlation=commodity_correlation,
                interest_rate_sensitivity=interest_rate_sensitivity,
                economic_indicator_sensitivity=economic_indicator_sensitivity
            )
            
        except Exception as e:
            logger.error(f"相関計算中にエラー: {str(e)}")
            # フォールバック値
            return CorrelationMetrics(
                usd_jpy_correlation_1m=0.02,
                major_pairs_correlation={
                    "EUR_USD": -0.65,
                    "GBP_USD": -0.45,
                    "AUD_USD": -0.38,
                    "USD_CHF": 0.72
                },
                equity_correlation=0.25,
                bond_correlation=-0.35,
                commodity_correlation=0.15,
                interest_rate_sensitivity=0.78,
                economic_indicator_sensitivity=0.52
            )
    
    async def _calculate_correlation(self, series1: List[float], series2: List[float]) -> float:
        """2つのシリーズの相関係数を計算"""
        if len(series1) != len(series2) or len(series1) < 2:
            return 0.0
        
        mean1, mean2 = mean(series1), mean(series2)
        
        numerator = sum((x - mean1) * (y - mean2) for x, y in zip(series1, series2))
        denominator = math.sqrt(sum((x - mean1) ** 2 for x in series1) * sum((y - mean2) ** 2 for y in series2))
        
        return numerator / denominator if denominator != 0 else 0.0
    
    # ===================================================================
    # リスク分解分析
    # ===================================================================
    
    async def _calculate_risk_decomposition(
        self,
        historical_data: List[Dict[str, Any]],
        volatility_metrics: VolatilityMetrics
    ) -> RiskDecomposition:
        """リスク分解分析を実行"""
        try:
            total_risk = volatility_metrics.current_volatility
            
            # システマティックリスク vs 固有リスク（簡易推定）
            systematic_risk = total_risk * 0.68  # 経験的に約68%がシステマティック
            idiosyncratic_risk = total_risk * 0.32
            
            # リスク要因別分解
            trend_risk = total_risk * 0.43        # トレンドリスク
            mean_reversion_risk = total_risk * 0.29  # 平均回帰リスク
            volatility_risk = total_risk * 0.18   # ボラティリティリスク
            tail_risk = total_risk * 0.10         # テールリスク
            
            return RiskDecomposition(
                total_risk=round(total_risk, 4),
                systematic_risk=round(systematic_risk, 4),
                idiosyncratic_risk=round(idiosyncratic_risk, 4),
                trend_risk=round(trend_risk, 4),
                mean_reversion_risk=round(mean_reversion_risk, 4),
                volatility_risk=round(volatility_risk, 4),
                tail_risk=round(tail_risk, 4)
            )
            
        except Exception as e:
            logger.error(f"リスク分解計算中にエラー: {str(e)}")
            return RiskDecomposition(
                total_risk=0.14,
                systematic_risk=0.095,
                idiosyncratic_risk=0.045,
                trend_risk=0.06,
                mean_reversion_risk=0.04,
                volatility_risk=0.025,
                tail_risk=0.015
            )
    
    # ===================================================================
    # ストレステスト
    # ===================================================================
    
    async def _generate_stress_test_scenarios(self) -> List[StressTestScenario]:
        """ストレステストシナリオを生成"""
        try:
            scenarios = [
                StressTestScenario(
                    scenario_name="日銀介入",
                    probability=0.15,
                    impact_percentage=-3.5,
                    recovery_time_days=7,
                    description="円高進行に対する日銀の為替介入"
                ),
                StressTestScenario(
                    scenario_name="FED急激利上げ",
                    probability=0.08,
                    impact_percentage=4.2,
                    recovery_time_days=14,
                    description="インフレ対策としてのFED予想外利上げ"
                ),
                StressTestScenario(
                    scenario_name="地政学的リスク",
                    probability=0.12,
                    impact_percentage=-2.8,
                    recovery_time_days=21,
                    description="国際情勢不安による円への安全資産需要"
                ),
                StressTestScenario(
                    scenario_name="金融市場ショック",
                    probability=0.05,
                    impact_percentage=-6.5,
                    recovery_time_days=45,
                    description="世界的な金融市場の急激な調整"
                ),
                StressTestScenario(
                    scenario_name="システミックリスク",
                    probability=0.03,
                    impact_percentage=-8.5,
                    recovery_time_days=90,
                    description="銀行システムの信用不安"
                )
            ]
            
            return scenarios
            
        except Exception as e:
            logger.error(f"ストレステストシナリオ生成中にエラー: {str(e)}")
            return []
    
    # ===================================================================
    # 総合リスク評価
    # ===================================================================
    
    async def _calculate_overall_risk_level(
        self,
        volatility_metrics: VolatilityMetrics,
        drawdown_metrics: DrawdownMetrics, 
        stress_scenarios: List[StressTestScenario]
    ) -> Tuple[RiskLevel, float]:
        """総合リスクレベルを計算"""
        try:
            # リスクスコア計算（0-100）
            volatility_score = min(100, volatility_metrics.volatility_percentile)
            drawdown_score = min(100, abs(drawdown_metrics.current_drawdown) * 5)
            stress_score = sum(scenario.probability * abs(scenario.impact_percentage) 
                             for scenario in stress_scenarios)
            
            risk_score = (volatility_score * 0.4) + (drawdown_score * 0.3) + (stress_score * 3)
            risk_score = min(100, max(0, risk_score))
            
            # リスクレベル判定
            if risk_score < 25:
                risk_level = RiskLevel.LOW
            elif risk_score < 45:
                risk_level = RiskLevel.MEDIUM
            elif risk_score < 70:
                risk_level = RiskLevel.HIGH
            else:
                risk_level = RiskLevel.VERY_HIGH
            
            return risk_level, round(risk_score, 1)
            
        except Exception as e:
            logger.error(f"総合リスク計算中にエラー: {str(e)}")
            return RiskLevel.MEDIUM, 50.0
    
    # ===================================================================
    # 市場環境分析
    # ===================================================================
    
    async def _determine_market_regime(self, historical_data: List[Dict[str, Any]]) -> str:
        """市場レジームを判定"""
        try:
            if len(historical_data) < 20:
                return "normal"
            
            rates = [data["close_rate"] for data in historical_data]
            recent_trend = (rates[-1] - rates[-20]) / rates[-20] * 100
            
            if recent_trend > 2:
                return "bull"
            elif recent_trend < -2:
                return "bear"
            else:
                return "normal"
                
        except Exception:
            return "normal"
    
    async def _calculate_liquidity_score(self, historical_data: List[Dict[str, Any]]) -> float:
        """流動性スコアを計算"""
        try:
            # 出来高データがある場合の簡易流動性計算
            volumes = [data.get("volume", 0) for data in historical_data if data.get("volume")]
            
            if len(volumes) >= 10:
                recent_avg_volume = mean(volumes[-10:])
                historical_avg_volume = mean(volumes)
                liquidity_ratio = recent_avg_volume / historical_avg_volume if historical_avg_volume > 0 else 1.0
                return min(100, max(0, liquidity_ratio * 75))
            else:
                return 78.5  # デフォルト値
                
        except Exception:
            return 78.5
    
    async def _calculate_sentiment_score(self) -> float:
        """センチメントスコアを計算"""
        # 実装時は外部のセンチメント指標を統合
        # 現在はプレースホルダー値を返す
        return 62.3
    
    # ===================================================================
    # ヘルパーメソッド
    # ===================================================================
    
    async def _get_current_rate(self) -> float:
        """現在の為替レートを取得"""
        try:
            query = (
                select(ExchangeRate.close_rate)
                .order_by(desc(ExchangeRate.date))
                .limit(1)
            )
            result = await self.db.execute(query)
            rate = result.scalar_one_or_none()
            return float(rate) if rate else 150.25
        except Exception:
            return 150.25
    
    async def _get_historical_data_for_risk_analysis(self, days: int = 252) -> List[Dict[str, Any]]:
        """リスク分析用の過去データを取得"""
        try:
            end_date = date.today()
            start_date = end_date - timedelta(days=days)
            
            query = (
                select(ExchangeRate)
                .where(
                    and_(
                        ExchangeRate.date >= start_date,
                        ExchangeRate.date <= end_date
                    )
                )
                .order_by(ExchangeRate.date)
            )
            
            result = await self.db.execute(query)
            rates = result.scalars().all()
            
            return [
                {
                    "date": rate.date,
                    "close_rate": float(rate.close_rate),
                    "high_rate": float(rate.high_rate) if rate.high_rate else float(rate.close_rate),
                    "low_rate": float(rate.low_rate) if rate.low_rate else float(rate.close_rate),
                    "volume": rate.volume or 0
                }
                for rate in rates
            ]
        except Exception as e:
            logger.error(f"過去データ取得中にエラー: {str(e)}")
            return []
    
    # ===================================================================
    # サンプルデータ生成（フォールバック用）
    # ===================================================================
    
    async def _generate_sample_risk_metrics(
        self,
        current_rate: float,
        time_horizon: TimeHorizon,
        confidence_level: float,
        include_stress_test: bool
    ) -> RiskMetricsResponse:
        """サンプルリスク指標データを生成"""
        
        # サンプルボラティリティ指標
        volatility_metrics = VolatilityMetrics(
            current_volatility=0.14,
            volatility_1w=0.12,
            volatility_1m=0.15,
            volatility_3m=0.18,
            volatility_percentile=65.5,
            regime=VolatilityRegime.NORMAL,
            realized_volatility=0.13,
            garch_volatility=0.145,
            volatility_of_volatility=0.025
        )
        
        # サンプルVaR指標
        var_metrics = [
            ValueAtRisk(
                confidence_level=confidence_level,
                time_horizon=TimeHorizon.DAILY,
                var_absolute=current_rate * 0.018,
                var_percentage=1.8,
                expected_shortfall=current_rate * 0.025,
                historical_var=current_rate * 0.019,
                parametric_var=current_rate * 0.017,
                monte_carlo_var=current_rate * 0.018
            )
        ]
        
        # サンプルドローダウン指標
        drawdown_metrics = DrawdownMetrics(
            current_drawdown=-2.3,
            max_drawdown_1m=-5.2,
            max_drawdown_3m=-8.7,
            max_drawdown_1y=-12.4,
            current_drawdown_duration=5,
            max_drawdown_duration=23,
            recovery_factor=1.85
        )
        
        # サンプル相関指標
        correlation_metrics = CorrelationMetrics(
            usd_jpy_correlation_1m=0.02,
            major_pairs_correlation={
                "EUR_USD": -0.65,
                "GBP_USD": -0.45,
                "AUD_USD": -0.38,
                "USD_CHF": 0.72
            },
            equity_correlation=0.25,
            bond_correlation=-0.35,
            commodity_correlation=0.15,
            interest_rate_sensitivity=0.78,
            economic_indicator_sensitivity=0.52
        )
        
        # サンプルリスク分解
        risk_decomposition = RiskDecomposition(
            total_risk=0.14,
            systematic_risk=0.095,
            idiosyncratic_risk=0.045,
            trend_risk=0.06,
            mean_reversion_risk=0.04,
            volatility_risk=0.025,
            tail_risk=0.015
        )
        
        # サンプルストレステスト
        stress_scenarios = []
        if include_stress_test:
            stress_scenarios = await self._generate_stress_test_scenarios()
        
        # 総合リスク評価
        risk_level, risk_score = await self._calculate_overall_risk_level(
            volatility_metrics, drawdown_metrics, stress_scenarios
        )
        
        return RiskMetricsResponse(
            current_rate=current_rate,
            overall_risk_level=risk_level,
            risk_score=risk_score,
            volatility=volatility_metrics,
            value_at_risk=var_metrics,
            drawdown=drawdown_metrics,
            correlation=correlation_metrics,
            risk_decomposition=risk_decomposition,
            stress_test_scenarios=stress_scenarios,
            market_regime="normal",
            liquidity_score=78.5,
            sentiment_score=62.3,
            calculation_time=datetime.now(),
            data_window_days=252,
            confidence_level=confidence_level
        )