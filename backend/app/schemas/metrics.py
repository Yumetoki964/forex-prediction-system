"""
Risk Metrics API Schema Definitions
===================================

Phase B-2aの対象エンドポイント用スキーマ:
- 1.4: /api/metrics/risk (GET) - リスク指標取得

リスク評価とボラティリティ分析に関するスキーマを定義
"""

from pydantic import BaseModel, Field, ConfigDict
from typing import List, Optional, Dict, Any
from datetime import datetime, date
from decimal import Decimal
from enum import Enum


class RiskLevel(str, Enum):
    """リスクレベルの列挙"""
    VERY_LOW = "very_low"
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    VERY_HIGH = "very_high"
    EXTREME = "extreme"


class VolatilityRegime(str, Enum):
    """ボラティリティ環境の列挙"""
    LOW = "low"            # 低ボラティリティ環境
    NORMAL = "normal"      # 通常ボラティリティ環境
    HIGH = "high"          # 高ボラティリティ環境
    EXTREME = "extreme"    # 極端ボラティリティ環境


class TimeHorizon(str, Enum):
    """リスク評価期間の列挙"""
    INTRADAY = "intraday"      # 日中
    DAILY = "daily"            # 日次
    WEEKLY = "weekly"          # 週次
    MONTHLY = "monthly"        # 月次
    QUARTERLY = "quarterly"    # 四半期


# ===================================================================
# 1.4: /api/metrics/risk (GET) - リスク指標取得
# ===================================================================

class VolatilityMetrics(BaseModel):
    """ボラティリティ指標"""
    current_volatility: float = Field(..., description="現在ボラティリティ（年率）", ge=0)
    volatility_1w: float = Field(..., description="1週間ボラティリティ", ge=0)
    volatility_1m: float = Field(..., description="1ヶ月ボラティリティ", ge=0)
    volatility_3m: float = Field(..., description="3ヶ月ボラティリティ", ge=0)
    volatility_percentile: float = Field(..., description="ボラティリティパーセンタイル（過去1年）", ge=0, le=100)
    regime: VolatilityRegime = Field(..., description="ボラティリティ環境")
    
    # 高度なボラティリティ指標
    realized_volatility: float = Field(..., description="実現ボラティリティ", ge=0)
    garch_volatility: Optional[float] = Field(None, description="GARCH予測ボラティリティ", ge=0)
    volatility_of_volatility: float = Field(..., description="ボラティリティのボラティリティ", ge=0)

    model_config = ConfigDict(from_attributes=True, protected_namespaces=())


class ValueAtRisk(BaseModel):
    """バリューアットリスク（VaR）指標"""
    confidence_level: float = Field(..., description="信頼水準", ge=0.90, le=0.99)
    time_horizon: TimeHorizon = Field(..., description="評価期間")
    var_absolute: float = Field(..., description="絶対VaR（円）")
    var_percentage: float = Field(..., description="相対VaR（%）", ge=0)
    expected_shortfall: float = Field(..., description="期待ショートフォール（ES）")
    
    # VaR計算手法別
    historical_var: float = Field(..., description="ヒストリカルVaR")
    parametric_var: float = Field(..., description="パラメトリックVaR")
    monte_carlo_var: Optional[float] = Field(None, description="モンテカルロVaR")

    model_config = ConfigDict(from_attributes=True, protected_namespaces=())


class DrawdownMetrics(BaseModel):
    """ドローダウン指標"""
    current_drawdown: float = Field(..., description="現在ドローダウン（%）", le=0)
    max_drawdown_1m: float = Field(..., description="1ヶ月最大ドローダウン（%）", le=0)
    max_drawdown_3m: float = Field(..., description="3ヶ月最大ドローダウン（%）", le=0)
    max_drawdown_1y: float = Field(..., description="1年最大ドローダウン（%）", le=0)
    
    # ドローダウン期間情報
    current_drawdown_duration: int = Field(..., description="現在ドローダウン継続日数", ge=0)
    max_drawdown_duration: int = Field(..., description="最大ドローダウン継続日数", ge=0)
    recovery_factor: float = Field(..., description="回復ファクター", ge=0)

    model_config = ConfigDict(from_attributes=True, protected_namespaces=())


class CorrelationMetrics(BaseModel):
    """相関・感応度指標"""
    usd_jpy_correlation_1m: float = Field(..., description="1ヶ月USD/JPY自己相関", ge=-1, le=1)
    major_pairs_correlation: Dict[str, float] = Field(..., description="主要通貨ペアとの相関")
    equity_correlation: float = Field(..., description="株式市場との相関", ge=-1, le=1)
    bond_correlation: float = Field(..., description="債券市場との相関", ge=-1, le=1)
    commodity_correlation: float = Field(..., description="商品市場との相関", ge=-1, le=1)
    
    # 感応度分析
    interest_rate_sensitivity: float = Field(..., description="金利感応度")
    economic_indicator_sensitivity: float = Field(..., description="経済指標感応度")

    model_config = ConfigDict(from_attributes=True, protected_namespaces=())


class StressTestScenario(BaseModel):
    """ストレステストシナリオ"""
    scenario_name: str = Field(..., description="シナリオ名")
    probability: float = Field(..., description="発生確率", ge=0, le=1)
    impact_percentage: float = Field(..., description="影響度（%）")
    recovery_time_days: int = Field(..., description="回復予想日数", ge=0)
    description: str = Field(..., description="シナリオ説明")

    model_config = ConfigDict(from_attributes=True, protected_namespaces=())


class RiskDecomposition(BaseModel):
    """リスク分解分析"""
    total_risk: float = Field(..., description="総リスク", ge=0)
    systematic_risk: float = Field(..., description="システマティックリスク", ge=0)
    idiosyncratic_risk: float = Field(..., description="固有リスク", ge=0)
    
    # リスク要因別分解
    trend_risk: float = Field(..., description="トレンドリスク", ge=0)
    mean_reversion_risk: float = Field(..., description="平均回帰リスク", ge=0)
    volatility_risk: float = Field(..., description="ボラティリティリスク", ge=0)
    tail_risk: float = Field(..., description="テールリスク", ge=0)

    model_config = ConfigDict(from_attributes=True, protected_namespaces=())


class RiskMetricsResponse(BaseModel):
    """リスク指標レスポンス"""
    current_rate: float = Field(..., description="現在レート", gt=0)
    overall_risk_level: RiskLevel = Field(..., description="総合リスクレベル")
    risk_score: float = Field(..., description="リスクスコア（0-100）", ge=0, le=100)
    
    # 主要リスク指標
    volatility: VolatilityMetrics = Field(..., description="ボラティリティ指標")
    value_at_risk: List[ValueAtRisk] = Field(..., description="VaR指標（複数信頼水準・期間）")
    drawdown: DrawdownMetrics = Field(..., description="ドローダウン指標")
    correlation: CorrelationMetrics = Field(..., description="相関指標")
    
    # 高度なリスク分析
    risk_decomposition: RiskDecomposition = Field(..., description="リスク分解")
    stress_test_scenarios: List[StressTestScenario] = Field(..., description="ストレステストシナリオ")
    
    # 市場環境情報
    market_regime: str = Field(..., description="市場環境（bull/bear/sideways/crisis）")
    liquidity_score: float = Field(..., description="流動性スコア", ge=0, le=100)
    sentiment_score: float = Field(..., description="センチメントスコア", ge=0, le=100)
    
    # メタデータ
    calculation_time: datetime = Field(..., description="計算実行時刻")
    data_window_days: int = Field(..., description="使用データ期間（日数）", gt=0)
    confidence_level: float = Field(0.95, description="計算信頼水準", ge=0, le=1)

    model_config = ConfigDict(from_attributes=True, protected_namespaces=())


# ===================================================================
# リスクアラート関連スキーマ
# ===================================================================

class RiskAlert(BaseModel):
    """リスクアラート"""
    alert_type: str = Field(..., description="アラートタイプ")
    severity: str = Field(..., description="深刻度（low/medium/high/critical）")
    message: str = Field(..., description="アラートメッセージ")
    threshold_breached: float = Field(..., description="突破した閾値")
    current_value: float = Field(..., description="現在値")
    triggered_at: datetime = Field(..., description="発生時刻")

    model_config = ConfigDict(from_attributes=True, protected_namespaces=())


class RiskSummary(BaseModel):
    """リスクサマリー"""
    risk_level: RiskLevel = Field(..., description="総合リスクレベル")
    key_risks: List[str] = Field(..., description="主要リスク要因")
    risk_outlook: str = Field(..., description="リスク見通し")
    recommended_actions: List[str] = Field(..., description="推奨アクション")
    active_alerts: List[RiskAlert] = Field(default_factory=list, description="アクティブアラート")

    model_config = ConfigDict(from_attributes=True, protected_namespaces=())