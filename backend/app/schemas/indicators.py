"""
Technical & Economic Indicators API Schema Definitions
=====================================================

Phase B-2aの対象エンドポイント用スキーマ:
- 2.3: /api/indicators/technical (GET) - テクニカル指標取得
- 2.4: /api/indicators/economic (GET) - 経済指標影響度取得

テクニカル分析および経済指標の影響度分析用スキーマを定義
"""

from pydantic import BaseModel, Field, ConfigDict
from typing import List, Optional, Dict, Any, Union
from datetime import datetime, date
from decimal import Decimal
from enum import Enum


class IndicatorSignal(str, Enum):
    """指標シグナルの列挙"""
    STRONG_SELL = "strong_sell"
    SELL = "sell"
    NEUTRAL = "neutral"
    BUY = "buy"
    STRONG_BUY = "strong_buy"


class TrendDirection(str, Enum):
    """トレンド方向の列挙"""
    UPWARD = "upward"
    DOWNWARD = "downward"
    SIDEWAYS = "sideways"
    UNKNOWN = "unknown"


class EconomicIndicatorCategory(str, Enum):
    """経済指標カテゴリの列挙"""
    MONETARY_POLICY = "monetary_policy"     # 金融政策
    EMPLOYMENT = "employment"               # 雇用
    INFLATION = "inflation"                 # インフレ
    GDP_GROWTH = "gdp_growth"              # GDP成長
    TRADE_BALANCE = "trade_balance"         # 貿易収支
    SENTIMENT = "sentiment"                 # 景況感
    FINANCIAL_MARKETS = "financial_markets" # 金融市場


# ===================================================================
# 2.3: /api/indicators/technical (GET) - テクニカル指標取得
# ===================================================================

class MovingAverageIndicator(BaseModel):
    """移動平均指標"""
    sma_5: Optional[float] = Field(None, description="5日単純移動平均", gt=0)
    sma_25: Optional[float] = Field(None, description="25日単純移動平均", gt=0)
    sma_75: Optional[float] = Field(None, description="75日単純移動平均", gt=0)
    ema_12: Optional[float] = Field(None, description="12日指数移動平均", gt=0)
    ema_26: Optional[float] = Field(None, description="26日指数移動平均", gt=0)
    
    # シグナル情報
    trend_signal: IndicatorSignal = Field(IndicatorSignal.NEUTRAL, description="トレンドシグナル")
    ma_crossover_signal: Optional[str] = Field(None, description="MA交差シグナル")
    price_vs_ma_signal: IndicatorSignal = Field(IndicatorSignal.NEUTRAL, description="価格対MA位置シグナル")

    model_config = ConfigDict(from_attributes=True, protected_namespaces=())


class OscillatorIndicator(BaseModel):
    """オシレーター指標"""
    rsi_14: Optional[float] = Field(None, description="14日RSI", ge=0, le=100)
    stochastic_k: Optional[float] = Field(None, description="ストキャスティクス%K", ge=0, le=100)
    stochastic_d: Optional[float] = Field(None, description="ストキャスティクス%D", ge=0, le=100)
    
    # オシレーターシグナル
    rsi_signal: IndicatorSignal = Field(IndicatorSignal.NEUTRAL, description="RSIシグナル")
    stoch_signal: IndicatorSignal = Field(IndicatorSignal.NEUTRAL, description="ストキャスティクスシグナル")
    divergence_signal: Optional[str] = Field(None, description="ダイバージェンスシグナル")
    
    # 過買い・過売り判定
    is_overbought: bool = Field(False, description="過買い状態")
    is_oversold: bool = Field(False, description="過売り状態")

    model_config = ConfigDict(from_attributes=True, protected_namespaces=())


class MomentumIndicator(BaseModel):
    """モメンタム指標"""
    macd: Optional[float] = Field(None, description="MACD線")
    macd_signal: Optional[float] = Field(None, description="MACDシグナル線")
    macd_histogram: Optional[float] = Field(None, description="MACDヒストグラム")
    
    # MACDシグナル
    macd_trend_signal: IndicatorSignal = Field(IndicatorSignal.NEUTRAL, description="MACDトレンドシグナル")
    macd_crossover: Optional[str] = Field(None, description="MACDクロスオーバー")
    histogram_momentum: str = Field("neutral", description="ヒストグラムモメンタム（increasing/decreasing/neutral）")

    model_config = ConfigDict(from_attributes=True, protected_namespaces=())


class VolatilityIndicator(BaseModel):
    """ボラティリティ指標"""
    bb_upper: Optional[float] = Field(None, description="ボリンジャーバンド上限", gt=0)
    bb_middle: Optional[float] = Field(None, description="ボリンジャーバンド中央線", gt=0)
    bb_lower: Optional[float] = Field(None, description="ボリンジャーバンド下限", gt=0)
    bb_width: Optional[float] = Field(None, description="ボリンジャーバンド幅", ge=0)
    atr_14: Optional[float] = Field(None, description="14日ATR", ge=0)
    volatility_20: Optional[float] = Field(None, description="20日ボラティリティ", ge=0)
    
    # ボラティリティシグナル
    bb_signal: IndicatorSignal = Field(IndicatorSignal.NEUTRAL, description="ボリンジャーバンドシグナル")
    squeeze_status: bool = Field(False, description="スクイーズ状態")
    volatility_regime: str = Field("normal", description="ボラティリティ環境")

    model_config = ConfigDict(from_attributes=True, protected_namespaces=())


class VolumeIndicator(BaseModel):
    """出来高指標"""
    current_volume: Optional[int] = Field(None, description="現在出来高", ge=0)
    volume_sma_20: Optional[float] = Field(None, description="20日出来高移動平均", ge=0)
    volume_ratio: Optional[float] = Field(None, description="出来高比率", ge=0)
    
    # 出来高シグナル
    volume_signal: str = Field("normal", description="出来高シグナル（low/normal/high/extreme）")
    price_volume_trend: Optional[str] = Field(None, description="価格出来高トレンド")

    model_config = ConfigDict(from_attributes=True, protected_namespaces=())


class TechnicalSummary(BaseModel):
    """テクニカル分析サマリー"""
    overall_signal: IndicatorSignal = Field(IndicatorSignal.NEUTRAL, description="総合シグナル")
    trend_direction: TrendDirection = Field(TrendDirection.SIDEWAYS, description="トレンド方向")
    trend_strength: float = Field(0.5, description="トレンド強度", ge=0, le=1)
    volatility_assessment: str = Field("normal", description="ボラティリティ評価")
    
    # 各カテゴリー評価
    trend_score: float = Field(0.5, description="トレンドスコア", ge=0, le=1)
    momentum_score: float = Field(0.5, description="モメンタムスコア", ge=0, le=1)
    volatility_score: float = Field(0.5, description="ボラティリティスコア", ge=0, le=1)
    volume_score: float = Field(0.5, description="出来高スコア", ge=0, le=1)

    model_config = ConfigDict(from_attributes=True, protected_namespaces=())


class TechnicalIndicatorsResponse(BaseModel):
    """テクニカル指標レスポンス"""
    current_rate: float = Field(..., description="現在レート", gt=0)
    analysis_date: date = Field(..., description="分析日")
    
    # 主要テクニカル指標
    moving_averages: MovingAverageIndicator = Field(..., description="移動平均指標")
    oscillators: OscillatorIndicator = Field(..., description="オシレーター指標")
    momentum: MomentumIndicator = Field(..., description="モメンタム指標")
    volatility: VolatilityIndicator = Field(..., description="ボラティリティ指標")
    volume: Optional[VolumeIndicator] = Field(None, description="出来高指標")
    
    # 分析サマリー
    technical_summary: TechnicalSummary = Field(..., description="テクニカル分析サマリー")
    
    # メタデータ
    calculation_time: datetime = Field(..., description="計算実行時刻")
    data_points_used: int = Field(..., description="使用データポイント数", gt=0)
    reliability_score: float = Field(1.0, description="信頼性スコア", ge=0, le=1)

    model_config = ConfigDict(from_attributes=True, protected_namespaces=())


# ===================================================================
# 2.4: /api/indicators/economic (GET) - 経済指標影響度取得
# ===================================================================

class EconomicIndicatorItem(BaseModel):
    """経済指標項目"""
    name: str = Field(..., description="指標名")
    category: EconomicIndicatorCategory = Field(..., description="カテゴリ")
    release_date: Optional[date] = Field(None, description="発表日")
    actual_value: Optional[float] = Field(None, description="実際値")
    forecast_value: Optional[float] = Field(None, description="予想値")
    previous_value: Optional[float] = Field(None, description="前回値")
    
    # 影響度評価
    importance: str = Field("medium", description="重要度（low/medium/high/critical）")
    impact_direction: str = Field("neutral", description="影響方向（positive/negative/neutral）")
    impact_magnitude: float = Field(0.5, description="影響度合い", ge=0, le=1)
    
    # 市場反応
    market_reaction: Optional[str] = Field(None, description="市場反応")
    volatility_impact: float = Field(0.0, description="ボラティリティ影響", ge=0)

    model_config = ConfigDict(from_attributes=True, protected_namespaces=())


class CentralBankPolicy(BaseModel):
    """中央銀行政策"""
    bank_name: str = Field(..., description="中央銀行名")
    current_rate: Optional[float] = Field(None, description="現在政策金利", ge=0)
    rate_change_probability: Dict[str, float] = Field(..., description="利上げ/利下げ確率")
    policy_stance: str = Field("neutral", description="政策スタンス（dovish/neutral/hawkish）")
    next_meeting_date: Optional[date] = Field(None, description="次回会合日")
    
    # 影響評価
    usd_jpy_impact: float = Field(0.0, description="USD/JPYへの影響度", ge=-1, le=1)
    confidence_level: float = Field(0.5, description="予測信頼度", ge=0, le=1)

    model_config = ConfigDict(from_attributes=True, protected_namespaces=())


class MacroeconomicTrend(BaseModel):
    """マクロ経済トレンド"""
    country: str = Field(..., description="国名")
    gdp_growth_trend: Optional[float] = Field(None, description="GDP成長トレンド")
    inflation_trend: Optional[float] = Field(None, description="インフレトレンド")
    employment_trend: Optional[float] = Field(None, description="雇用トレンド")
    
    # 相対評価
    economic_strength_vs_us: float = Field(0.0, description="対米経済力", ge=-1, le=1)
    currency_outlook: str = Field("neutral", description="通貨見通し（bearish/neutral/bullish）")

    model_config = ConfigDict(from_attributes=True, protected_namespaces=())


class MarketSentimentIndicator(BaseModel):
    """市場センチメント指標"""
    fear_greed_index: Optional[float] = Field(None, description="恐怖・貪欲指数", ge=0, le=100)
    vix_level: Optional[float] = Field(None, description="VIX水準", ge=0)
    risk_on_off_signal: str = Field("neutral", description="リスクオン・オフシグナル")
    
    # JPY特有のセンチメント
    safe_haven_demand: float = Field(0.5, description="安全資産需要", ge=0, le=1)
    carry_trade_appetite: float = Field(0.5, description="キャリートレード需要", ge=0, le=1)

    model_config = ConfigDict(from_attributes=True, protected_namespaces=())


class GeopoliticalRisk(BaseModel):
    """地政学的リスク"""
    risk_level: str = Field("normal", description="リスクレベル（low/normal/elevated/high/extreme）")
    risk_factors: List[str] = Field(default_factory=list, description="リスク要因")
    usd_jpy_impact: float = Field(0.0, description="USD/JPYへの影響", ge=-1, le=1)
    impact_probability: float = Field(0.1, description="影響発現確率", ge=0, le=1)
    
    # 時間軸
    short_term_impact: float = Field(0.0, description="短期影響", ge=-1, le=1)
    medium_term_impact: float = Field(0.0, description="中期影響", ge=-1, le=1)

    model_config = ConfigDict(from_attributes=True, protected_namespaces=())


class EconomicCalendar(BaseModel):
    """経済カレンダー"""
    upcoming_events: List[EconomicIndicatorItem] = Field(..., description="今後のイベント")
    high_impact_events_7d: List[EconomicIndicatorItem] = Field(..., description="7日以内の高インパクトイベント")
    event_impact_analysis: Dict[str, float] = Field(..., description="イベント影響分析")

    model_config = ConfigDict(from_attributes=True, protected_namespaces=())


class EconomicImpactResponse(BaseModel):
    """経済指標影響度レスポンス"""
    analysis_date: date = Field(..., description="分析日")
    overall_economic_sentiment: str = Field("neutral", description="総合経済センチメント")
    usd_strength_score: float = Field(0.5, description="USD強度スコア", ge=0, le=1)
    jpy_strength_score: float = Field(0.5, description="JPY強度スコア", ge=0, le=1)
    
    # 主要分析要素
    recent_indicators: List[EconomicIndicatorItem] = Field(..., description="直近の経済指標")
    central_bank_policies: List[CentralBankPolicy] = Field(..., description="中央銀行政策")
    macro_trends: List[MacroeconomicTrend] = Field(..., description="マクロ経済トレンド")
    market_sentiment: MarketSentimentIndicator = Field(..., description="市場センチメント")
    geopolitical_risks: List[GeopoliticalRisk] = Field(default_factory=list, description="地政学的リスク")
    
    # カレンダー情報
    economic_calendar: EconomicCalendar = Field(..., description="経済カレンダー")
    
    # 影響度サマリー
    top_positive_factors: List[str] = Field(..., description="主要ポジティブ要因")
    top_negative_factors: List[str] = Field(..., description="主要ネガティブ要因")
    key_risk_factors: List[str] = Field(..., description="主要リスク要因")
    
    # メタデータ
    data_sources: List[str] = Field(..., description="データソース")
    last_updated: datetime = Field(..., description="最終更新時刻")
    reliability_score: float = Field(1.0, description="信頼性スコア", ge=0, le=1)

    model_config = ConfigDict(from_attributes=True, protected_namespaces=())


# ===================================================================
# 共通ユーティリティスキーマ
# ===================================================================

class IndicatorAlert(BaseModel):
    """指標アラート"""
    indicator_type: str = Field(..., description="指標タイプ")
    alert_level: str = Field(..., description="アラートレベル（info/warning/critical）")
    message: str = Field(..., description="アラートメッセージ")
    triggered_at: datetime = Field(..., description="発生時刻")

    model_config = ConfigDict(from_attributes=True, protected_namespaces=())


class IndicatorConfiguration(BaseModel):
    """指標設定"""
    technical_indicators_enabled: List[str] = Field(..., description="有効なテクニカル指標")
    economic_indicators_priority: List[str] = Field(..., description="優先経済指標")
    alert_thresholds: Dict[str, float] = Field(..., description="アラート閾値")
    update_frequency_minutes: int = Field(60, description="更新頻度（分）", gt=0)

    model_config = ConfigDict(from_attributes=True, protected_namespaces=())