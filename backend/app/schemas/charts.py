"""
Historical Charts API Schema Definitions
========================================

Phase B-2aの対象エンドポイント用スキーマ:
- 2.1: /api/charts/historical (GET) - 履歴チャートデータ取得

為替レートの履歴チャートデータとテクニカル指標表示用のスキーマを定義
"""

from pydantic import BaseModel, Field, ConfigDict
from typing import List, Optional, Dict, Any
from datetime import datetime, date
from enum import Enum


class ChartTimeframe(str, Enum):
    """チャート時間軸の列挙"""
    ONE_MINUTE = "1m"
    FIVE_MINUTES = "5m"
    FIFTEEN_MINUTES = "15m"
    THIRTY_MINUTES = "30m"
    ONE_HOUR = "1h"
    FOUR_HOURS = "4h"
    DAILY = "1d"
    WEEKLY = "1w"
    MONTHLY = "1M"


class ChartPeriod(str, Enum):
    """チャート期間の列挙"""
    ONE_WEEK = "1week"
    TWO_WEEKS = "2weeks"
    ONE_MONTH = "1month"
    THREE_MONTHS = "3months"
    SIX_MONTHS = "6months"
    ONE_YEAR = "1year"
    TWO_YEARS = "2years"
    THREE_YEARS = "3years"
    FIVE_YEARS = "5years"
    ALL = "all"


class TechnicalIndicatorType(str, Enum):
    """テクニカル指標タイプの列挙"""
    SMA = "sma"
    EMA = "ema"
    WMA = "wma"
    RSI = "rsi"
    MACD = "macd"
    STOCHASTIC = "stochastic"
    BOLLINGER_BANDS = "bollinger_bands"
    ATR = "atr"
    FIBONACCI = "fibonacci"
    SUPPORT_RESISTANCE = "support_resistance"


# ===================================================================
# 2.1: /api/charts/historical (GET) - 履歴チャートデータ取得
# ===================================================================

class CandlestickData(BaseModel):
    """ローソク足データ"""
    timestamp: datetime = Field(..., description="時刻")
    date: date = Field(..., description="日付")
    open_rate: float = Field(..., description="始値", gt=0)
    high_rate: float = Field(..., description="高値", gt=0)
    low_rate: float = Field(..., description="安値", gt=0)
    close_rate: float = Field(..., description="終値", gt=0)
    volume: Optional[int] = Field(None, description="出来高", ge=0)
    
    # データ品質情報
    is_interpolated: bool = Field(False, description="補間データフラグ")
    is_holiday: bool = Field(False, description="祝日フラグ")
    source: str = Field("yahoo_finance", description="データソース")

    model_config = ConfigDict(from_attributes=True, protected_namespaces=())


class MovingAverageData(BaseModel):
    """移動平均データ"""
    timestamp: datetime = Field(..., description="時刻")
    sma_5: Optional[float] = Field(None, description="5期間単純移動平均", gt=0)
    sma_25: Optional[float] = Field(None, description="25期間単純移動平均", gt=0)
    sma_75: Optional[float] = Field(None, description="75期間単純移動平均", gt=0)
    ema_12: Optional[float] = Field(None, description="12期間指数移動平均", gt=0)
    ema_26: Optional[float] = Field(None, description="26期間指数移動平均", gt=0)

    model_config = ConfigDict(from_attributes=True, protected_namespaces=())


class RSIData(BaseModel):
    """RSIデータ"""
    timestamp: datetime = Field(..., description="時刻")
    rsi_14: Optional[float] = Field(None, description="14期間RSI", ge=0, le=100)
    rsi_signal: str = Field("neutral", description="RSIシグナル（oversold/neutral/overbought）")

    model_config = ConfigDict(from_attributes=True, protected_namespaces=())


class MACDData(BaseModel):
    """MACDデータ"""
    timestamp: datetime = Field(..., description="時刻")
    macd: Optional[float] = Field(None, description="MACD線")
    signal: Optional[float] = Field(None, description="シグナル線")
    histogram: Optional[float] = Field(None, description="ヒストグラム")
    macd_signal: str = Field("neutral", description="MACDシグナル（bullish/neutral/bearish）")

    model_config = ConfigDict(from_attributes=True, protected_namespaces=())


class BollingerBandsData(BaseModel):
    """ボリンジャーバンドデータ"""
    timestamp: datetime = Field(..., description="時刻")
    upper_band: Optional[float] = Field(None, description="上部バンド", gt=0)
    middle_band: Optional[float] = Field(None, description="中央線（SMA20）", gt=0)
    lower_band: Optional[float] = Field(None, description="下部バンド", gt=0)
    band_width: Optional[float] = Field(None, description="バンド幅", ge=0)
    squeeze_signal: bool = Field(False, description="スクイーズシグナル")

    model_config = ConfigDict(from_attributes=True, protected_namespaces=())


class StochasticData(BaseModel):
    """ストキャスティクスデータ"""
    timestamp: datetime = Field(..., description="時刻")
    stoch_k: Optional[float] = Field(None, description="ストキャスティクス%K", ge=0, le=100)
    stoch_d: Optional[float] = Field(None, description="ストキャスティクス%D", ge=0, le=100)
    stoch_signal: str = Field("neutral", description="ストキャスティクスシグナル（oversold/neutral/overbought）")

    model_config = ConfigDict(from_attributes=True, protected_namespaces=())


class ATRData(BaseModel):
    """ATR（Average True Range）データ"""
    timestamp: datetime = Field(..., description="時刻")
    atr_14: Optional[float] = Field(None, description="14期間ATR", ge=0)
    volatility_20: Optional[float] = Field(None, description="20日ボラティリティ", ge=0)
    volatility_regime: str = Field("normal", description="ボラティリティ環境（low/normal/high/extreme）")

    model_config = ConfigDict(from_attributes=True, protected_namespaces=())


class SupportResistanceLevel(BaseModel):
    """サポート・レジスタンスレベル"""
    level: float = Field(..., description="価格レベル", gt=0)
    level_type: str = Field(..., description="タイプ（support/resistance）")
    strength: float = Field(..., description="強度", ge=0, le=1)
    touch_count: int = Field(..., description="接触回数", ge=0)
    last_touch_date: Optional[date] = Field(None, description="最終接触日")

    model_config = ConfigDict(from_attributes=True, protected_namespaces=())


class FibonacciLevel(BaseModel):
    """フィボナッチリトレースメントレベル"""
    level: float = Field(..., description="価格レベル", gt=0)
    ratio: float = Field(..., description="フィボナッチ比率")
    label: str = Field(..., description="レベルラベル（0%, 23.6%, 38.2%等）")

    model_config = ConfigDict(from_attributes=True, protected_namespaces=())


class TrendlineData(BaseModel):
    """トレンドラインデータ"""
    start_date: date = Field(..., description="開始日")
    end_date: date = Field(..., description="終了日")
    start_price: float = Field(..., description="開始価格", gt=0)
    end_price: float = Field(..., description="終了価格", gt=0)
    trend_type: str = Field(..., description="タイプ（uptrend/downtrend）")
    strength: float = Field(..., description="強度", ge=0, le=1)
    break_probability: float = Field(..., description="ブレイク確率", ge=0, le=1)

    model_config = ConfigDict(from_attributes=True, protected_namespaces=())


class ChartAnnotation(BaseModel):
    """チャート注釈"""
    timestamp: datetime = Field(..., description="時刻")
    price_level: float = Field(..., description="価格レベル", gt=0)
    annotation_type: str = Field(..., description="注釈タイプ（signal/event/news）")
    text: str = Field(..., description="注釈テキスト")
    importance: str = Field("medium", description="重要度（low/medium/high/critical）")

    model_config = ConfigDict(from_attributes=True, protected_namespaces=())


class HistoricalChartResponse(BaseModel):
    """履歴チャートレスポンス"""
    # 基本パラメータ
    timeframe: ChartTimeframe = Field(..., description="時間軸")
    period: ChartPeriod = Field(..., description="期間")
    start_date: date = Field(..., description="開始日")
    end_date: date = Field(..., description="終了日")
    
    # 価格データ
    candlestick_data: List[CandlestickData] = Field(..., description="ローソク足データ")
    
    # テクニカル指標データ（オプショナル）
    moving_averages: Optional[List[MovingAverageData]] = Field(None, description="移動平均データ")
    rsi_data: Optional[List[RSIData]] = Field(None, description="RSIデータ")
    macd_data: Optional[List[MACDData]] = Field(None, description="MACDデータ")
    bollinger_bands: Optional[List[BollingerBandsData]] = Field(None, description="ボリンジャーバンド")
    stochastic_data: Optional[List[StochasticData]] = Field(None, description="ストキャスティクス")
    atr_data: Optional[List[ATRData]] = Field(None, description="ATRデータ")
    
    # チャート分析要素
    support_resistance: List[SupportResistanceLevel] = Field(default_factory=list, description="サポート・レジスタンスレベル")
    fibonacci_levels: List[FibonacciLevel] = Field(default_factory=list, description="フィボナッチレベル")
    trend_lines: List[TrendlineData] = Field(default_factory=list, description="トレンドライン")
    annotations: List[ChartAnnotation] = Field(default_factory=list, description="チャート注釈")
    
    # 統計情報
    total_data_points: int = Field(..., description="総データポイント数", ge=0)
    missing_data_points: int = Field(0, description="欠損データポイント数", ge=0)
    interpolated_points: int = Field(0, description="補間データポイント数", ge=0)
    data_quality_score: float = Field(1.0, description="データ品質スコア", ge=0, le=1)
    
    # メタデータ
    generated_at: datetime = Field(..., description="生成時刻")
    processing_time_ms: Optional[int] = Field(None, description="処理時間（ミリ秒）", ge=0)
    cache_hit: bool = Field(False, description="キャッシュヒット")

    model_config = ConfigDict(from_attributes=True, protected_namespaces=())


# ===================================================================
# チャートクエリパラメータ用スキーマ
# ===================================================================

class ChartQueryParams(BaseModel):
    """チャートクエリパラメータ"""
    period: ChartPeriod = Field(ChartPeriod.THREE_MONTHS, description="表示期間")
    timeframe: ChartTimeframe = Field(ChartTimeframe.DAILY, description="時間軸")
    indicators: List[TechnicalIndicatorType] = Field(default_factory=list, description="表示するテクニカル指標")
    include_volume: bool = Field(True, description="出来高を含める")
    include_support_resistance: bool = Field(False, description="サポート・レジスタンスレベルを含める")
    include_fibonacci: bool = Field(False, description="フィボナッチレベルを含める")
    include_trendlines: bool = Field(False, description="トレンドラインを含める")
    
    model_config = ConfigDict(from_attributes=True, protected_namespaces=())


class ChartConfiguration(BaseModel):
    """チャート設定"""
    chart_type: str = Field("candlestick", description="チャートタイプ（candlestick/line/area）")
    color_scheme: str = Field("default", description="カラースキーム（default/dark/light）")
    grid_enabled: bool = Field(True, description="グリッド表示")
    crosshair_enabled: bool = Field(True, description="十字線表示")
    tooltip_enabled: bool = Field(True, description="ツールチップ表示")
    zoom_enabled: bool = Field(True, description="ズーム機能")
    
    model_config = ConfigDict(from_attributes=True, protected_namespaces=())