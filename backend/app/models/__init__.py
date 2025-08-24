"""
Forex Prediction System - SQLAlchemy Models
============================================

このファイルは為替予測システムの全データモデルを定義する単一真実源です。
SQLAlchemy 2.0の非同期対応とPostgreSQL 15+の機能を活用して設計されています。

主要エンティティ:
1. ExchangeRate: 為替レートデータ（日次終値、高値、安値、出来高など）
2. Prediction: 予測結果（予測値、信頼区間、シグナルなど）
3. BacktestResult: バックテスト結果
4. DataSource: データソース管理
5. AlertSetting: アラート設定
6. PredictionSetting: 予測設定
7. TradingSignal: 売買シグナル
8. DataQuality: データ品質監視
"""

from datetime import datetime, date
from decimal import Decimal
from typing import Optional
from enum import Enum as PyEnum

from sqlalchemy import (
    Column, Integer, String, Float, Date, DateTime, BigInteger, 
    Text, Boolean, DECIMAL, ForeignKey, UniqueConstraint, Index,
    CheckConstraint, Enum
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

Base = declarative_base()

# ===================================================================
# Enums
# ===================================================================

class UserRole(PyEnum):
    ADMIN = "admin"
    USER = "user"

class SignalType(PyEnum):
    STRONG_SELL = "strong_sell"
    SELL = "sell"
    HOLD = "hold"
    BUY = "buy"
    STRONG_BUY = "strong_buy"

class PredictionPeriod(PyEnum):
    ONE_WEEK = "1week"
    TWO_WEEKS = "2weeks"
    THREE_WEEKS = "3weeks"
    ONE_MONTH = "1month"

class DataSourceType(PyEnum):
    BOJ_CSV = "boj_csv"           # 日銀CSV
    YAHOO_FINANCE = "yahoo_finance"  # Yahoo Finance
    ALPHA_VANTAGE = "alpha_vantage"  # Alpha Vantage API
    SCRAPING = "scraping"         # Web scraping

class DataSourceStatus(PyEnum):
    ACTIVE = "active"
    INACTIVE = "inactive"
    ERROR = "error"
    MAINTENANCE = "maintenance"

class AlertType(PyEnum):
    RATE_THRESHOLD = "rate_threshold"
    SIGNAL_CHANGE = "signal_change"
    VOLATILITY_HIGH = "volatility_high"
    PREDICTION_CONFIDENCE_LOW = "prediction_confidence_low"

class PredictionModel(PyEnum):
    LSTM = "lstm"
    XGBOOST = "xgboost"
    ENSEMBLE = "ensemble"

class BacktestStatus(PyEnum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"

# ===================================================================
# 為替レートデータモデル
# ===================================================================

class ExchangeRate(Base):
    """
    為替レートデータテーブル
    
    1990年からの日次ドル円為替レートを格納する中核テーブル。
    複数データソースからの情報を統合し、データ品質を保証。
    """
    __tablename__ = "exchange_rates"
    
    id = Column(Integer, primary_key=True, index=True)
    date = Column(Date, unique=True, nullable=False, index=True)
    
    # OHLC データ
    open_rate = Column(DECIMAL(10, 4), nullable=True)    # 始値
    high_rate = Column(DECIMAL(10, 4), nullable=True)    # 高値
    low_rate = Column(DECIMAL(10, 4), nullable=True)     # 安値
    close_rate = Column(DECIMAL(10, 4), nullable=False)  # 終値（メインレート）
    
    # 追加データ
    volume = Column(BigInteger, nullable=True)           # 出来高
    
    # メタデータ
    source = Column(Enum(DataSourceType), nullable=False, default=DataSourceType.YAHOO_FINANCE)
    is_holiday = Column(Boolean, default=False)         # 祝日フラグ
    is_interpolated = Column(Boolean, default=False)    # 補間データフラグ
    
    # タイムスタンプ
    created_at = Column(DateTime, default=func.now(), nullable=False)
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now(), nullable=False)
    
    # インデックス
    __table_args__ = (
        Index('idx_exchange_rates_date_source', 'date', 'source'),
        Index('idx_exchange_rates_created_at', 'created_at'),
        CheckConstraint('open_rate > 0', name='check_open_rate_positive'),
        CheckConstraint('high_rate > 0', name='check_high_rate_positive'),
        CheckConstraint('low_rate > 0', name='check_low_rate_positive'),
        CheckConstraint('close_rate > 0', name='check_close_rate_positive'),
        CheckConstraint('high_rate >= low_rate', name='check_high_low_relationship'),
    )

# ===================================================================
# 予測結果モデル
# ===================================================================

class Prediction(Base):
    """
    為替予測結果テーブル
    
    機械学習モデルによる1週間〜1ヶ月先の予測データを格納。
    信頼区間とボラティリティを含む統計的予測情報を提供。
    """
    __tablename__ = "predictions"
    
    id = Column(Integer, primary_key=True, index=True)
    
    # 予測日時
    prediction_date = Column(Date, nullable=False, index=True)      # 予測実行日
    target_date = Column(Date, nullable=False, index=True)          # 予測対象日
    period = Column(Enum(PredictionPeriod), nullable=False)         # 予測期間
    
    # 予測値
    predicted_rate = Column(DECIMAL(10, 4), nullable=False)         # 予測レート
    confidence_interval_lower = Column(DECIMAL(10, 4), nullable=True) # 信頼区間下限
    confidence_interval_upper = Column(DECIMAL(10, 4), nullable=True) # 信頼区間上限
    confidence_level = Column(Float, nullable=False, default=0.95)   # 信頼水準
    
    # リスク指標
    volatility = Column(Float, nullable=True)                       # ボラティリティ
    prediction_strength = Column(Float, nullable=False, default=0.5) # 予測強度（0-1）
    
    # モデル情報
    model_type = Column(Enum(PredictionModel), nullable=False, default=PredictionModel.ENSEMBLE)
    model_version = Column(String(50), nullable=False)
    feature_importance = Column(Text, nullable=True)               # JSON形式の特徴量重要度
    
    # タイムスタンプ
    created_at = Column(DateTime, default=func.now(), nullable=False)
    
    # インデックス
    __table_args__ = (
        Index('idx_predictions_date_period', 'prediction_date', 'period'),
        Index('idx_predictions_target_date', 'target_date'),
        Index('idx_predictions_model', 'model_type', 'model_version'),
        CheckConstraint('predicted_rate > 0', name='check_predicted_rate_positive'),
        CheckConstraint('confidence_level > 0 AND confidence_level <= 1', name='check_confidence_level_range'),
        CheckConstraint('prediction_strength >= 0 AND prediction_strength <= 1', name='check_prediction_strength_range'),
        CheckConstraint('confidence_interval_upper >= confidence_interval_lower', name='check_confidence_interval_order'),
        UniqueConstraint('prediction_date', 'target_date', 'model_type', name='unique_prediction_per_date_model'),
    )

# ===================================================================
# 売買シグナルモデル
# ===================================================================

class TradingSignal(Base):
    """
    売買シグナルテーブル
    
    5段階の売買判定（強い売り〜強い買い）と根拠情報を格納。
    テクニカル分析と予測結果を組み合わせたシグナル生成。
    """
    __tablename__ = "trading_signals"
    
    id = Column(Integer, primary_key=True, index=True)
    date = Column(Date, nullable=False, index=True)
    
    # シグナル情報
    signal_type = Column(Enum(SignalType), nullable=False)
    confidence = Column(Float, nullable=False, default=0.5)         # シグナル信頼度（0-1）
    strength = Column(Float, nullable=False, default=0.5)           # シグナル強度（0-1）
    
    # 根拠情報
    reasoning = Column(Text, nullable=True)                         # シグナル根拠（JSON形式）
    technical_score = Column(Float, nullable=True)                  # テクニカル分析スコア
    prediction_score = Column(Float, nullable=True)                 # 予測分析スコア
    
    # 関連データ
    prediction_id = Column(Integer, ForeignKey('predictions.id'), nullable=True)
    current_rate = Column(DECIMAL(10, 4), nullable=False)
    
    # タイムスタンプ
    created_at = Column(DateTime, default=func.now(), nullable=False)
    
    # リレーション
    prediction = relationship("Prediction", backref="signals")
    
    # インデックス
    __table_args__ = (
        Index('idx_trading_signals_date_signal', 'date', 'signal_type'),
        Index('idx_trading_signals_confidence', 'confidence'),
        CheckConstraint('confidence >= 0 AND confidence <= 1', name='check_signal_confidence_range'),
        CheckConstraint('strength >= 0 AND strength <= 1', name='check_signal_strength_range'),
        CheckConstraint('current_rate > 0', name='check_current_rate_positive'),
        UniqueConstraint('date', name='unique_signal_per_date'),
    )

# ===================================================================
# バックテスト結果モデル
# ===================================================================

class BacktestResult(Base):
    """
    バックテスト結果テーブル
    
    過去データを使用した予測精度検証とパフォーマンス分析結果を格納。
    リスク調整済みリターンとドローダウン分析を含む。
    """
    __tablename__ = "backtest_results"
    
    id = Column(Integer, primary_key=True, index=True)
    
    # バックテスト設定
    job_id = Column(String(100), unique=True, nullable=False, index=True)
    start_date = Column(Date, nullable=False)
    end_date = Column(Date, nullable=False)
    initial_capital = Column(DECIMAL(15, 2), nullable=False, default=1000000)  # 初期資金100万円
    
    # モデル設定
    model_type = Column(Enum(PredictionModel), nullable=False)
    model_config = Column(Text, nullable=True)              # JSON形式の設定
    
    # 実行情報
    status = Column(Enum(BacktestStatus), nullable=False, default=BacktestStatus.PENDING)
    execution_time = Column(Integer, nullable=True)         # 実行時間（秒）
    
    # パフォーマンス指標
    total_return = Column(DECIMAL(15, 4), nullable=True)     # 総リターン
    annualized_return = Column(DECIMAL(10, 4), nullable=True) # 年率リターン
    volatility = Column(DECIMAL(10, 4), nullable=True)       # ボラティリティ
    sharpe_ratio = Column(DECIMAL(10, 4), nullable=True)     # シャープレシオ
    max_drawdown = Column(DECIMAL(10, 4), nullable=True)     # 最大ドローダウン
    
    # 取引統計
    total_trades = Column(Integer, nullable=True)            # 総取引数
    winning_trades = Column(Integer, nullable=True)          # 勝ちトレード数
    losing_trades = Column(Integer, nullable=True)           # 負けトレード数
    win_rate = Column(DECIMAL(5, 4), nullable=True)         # 勝率
    
    # 予測精度
    prediction_accuracy_1w = Column(DECIMAL(5, 4), nullable=True)  # 1週間予測精度
    prediction_accuracy_2w = Column(DECIMAL(5, 4), nullable=True)  # 2週間予測精度
    prediction_accuracy_3w = Column(DECIMAL(5, 4), nullable=True)  # 3週間予測精度
    prediction_accuracy_1m = Column(DECIMAL(5, 4), nullable=True)  # 1ヶ月予測精度
    
    # メタデータ
    trade_log = Column(Text, nullable=True)                  # 取引履歴（JSON形式）
    error_message = Column(Text, nullable=True)              # エラーメッセージ
    
    # タイムスタンプ
    created_at = Column(DateTime, default=func.now(), nullable=False)
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now(), nullable=False)
    completed_at = Column(DateTime, nullable=True)
    
    # インデックス
    __table_args__ = (
        Index('idx_backtest_start_end_date', 'start_date', 'end_date'),
        Index('idx_backtest_model_type', 'model_type'),
        Index('idx_backtest_status', 'status'),
        CheckConstraint('initial_capital > 0', name='check_initial_capital_positive'),
        CheckConstraint('end_date > start_date', name='check_date_order'),
        CheckConstraint('win_rate >= 0 AND win_rate <= 1', name='check_win_rate_range'),
    )

# ===================================================================
# データソース管理モデル
# ===================================================================

class DataSource(Base):
    """
    データソース管理テーブル
    
    複数の為替データ取得ソースの設定と監視状況を管理。
    フォールバック機能とヘルスチェック結果を含む。
    """
    __tablename__ = "data_sources"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), unique=True, nullable=False)
    source_type = Column(Enum(DataSourceType), nullable=False)
    
    # 接続設定
    url = Column(String(500), nullable=True)
    api_key = Column(String(200), nullable=True)            # 暗号化推奨
    config = Column(Text, nullable=True)                    # JSON形式の設定
    
    # 監視情報
    status = Column(Enum(DataSourceStatus), nullable=False, default=DataSourceStatus.ACTIVE)
    priority = Column(Integer, nullable=False, default=1)   # 優先度（1が最高）
    
    # パフォーマンス指標
    success_rate = Column(DECIMAL(5, 4), nullable=False, default=1.0)  # 成功率
    avg_response_time = Column(Integer, nullable=True)      # 平均レスポンス時間（ms）
    last_success_at = Column(DateTime, nullable=True)
    last_failure_at = Column(DateTime, nullable=True)
    failure_count = Column(Integer, nullable=False, default=0)
    
    # レート制限
    rate_limit_requests = Column(Integer, nullable=True)    # リクエスト数制限
    rate_limit_period = Column(Integer, nullable=True)      # 制限期間（秒）
    daily_request_count = Column(Integer, nullable=False, default=0)
    last_request_at = Column(DateTime, nullable=True)
    
    # タイムスタンプ
    created_at = Column(DateTime, default=func.now(), nullable=False)
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now(), nullable=False)
    
    # インデックス
    __table_args__ = (
        Index('idx_data_sources_type_priority', 'source_type', 'priority'),
        Index('idx_data_sources_status', 'status'),
        CheckConstraint('priority > 0', name='check_priority_positive'),
        CheckConstraint('success_rate >= 0 AND success_rate <= 1', name='check_success_rate_range'),
        CheckConstraint('failure_count >= 0', name='check_failure_count_non_negative'),
    )

# ===================================================================
# アラート設定モデル
# ===================================================================

class AlertSetting(Base):
    """
    アラート設定テーブル
    
    ユーザー固有のアラート条件とメール・ブラウザ通知設定を管理。
    閾値ベースと条件ベースのアラート機能を提供。
    """
    __tablename__ = "alert_settings"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    alert_type = Column(Enum(AlertType), nullable=False)
    
    # アラート条件
    is_enabled = Column(Boolean, default=True, nullable=False)
    conditions = Column(Text, nullable=False)               # JSON形式の条件設定
    
    # 通知設定
    email_enabled = Column(Boolean, default=False)
    browser_notification_enabled = Column(Boolean, default=True)
    email_address = Column(String(255), nullable=True)
    
    # 実行制御
    cooldown_minutes = Column(Integer, default=60)          # クールダウン期間
    max_alerts_per_day = Column(Integer, default=10)        # 1日最大アラート数
    
    # 統計情報
    triggered_count = Column(Integer, default=0)
    last_triggered_at = Column(DateTime, nullable=True)
    
    # タイムスタンプ
    created_at = Column(DateTime, default=func.now(), nullable=False)
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now(), nullable=False)
    
    # インデックス
    __table_args__ = (
        Index('idx_alert_settings_type_enabled', 'alert_type', 'is_enabled'),
        CheckConstraint('cooldown_minutes >= 0', name='check_cooldown_non_negative'),
        CheckConstraint('max_alerts_per_day > 0', name='check_max_alerts_positive'),
    )

# ===================================================================
# アクティブアラートモデル
# ===================================================================

class ActiveAlert(Base):
    """
    アクティブアラートテーブル
    
    発生中のアラートと通知履歴を管理。
    アラート設定に基づく自動生成と手動確認機能を提供。
    """
    __tablename__ = "active_alerts"
    
    id = Column(Integer, primary_key=True, index=True)
    alert_setting_id = Column(Integer, ForeignKey('alert_settings.id'), nullable=False)
    
    # アラート情報
    title = Column(String(200), nullable=False)
    message = Column(Text, nullable=False)
    severity = Column(String(20), default='medium')         # low, medium, high, critical
    
    # 状態管理
    is_acknowledged = Column(Boolean, default=False)
    acknowledged_at = Column(DateTime, nullable=True)
    
    # 関連データ
    exchange_rate_id = Column(Integer, ForeignKey('exchange_rates.id'), nullable=True)
    prediction_id = Column(Integer, ForeignKey('predictions.id'), nullable=True)
    
    # タイムスタンプ
    created_at = Column(DateTime, default=func.now(), nullable=False)
    
    # リレーション
    alert_setting = relationship("AlertSetting", backref="active_alerts")
    exchange_rate = relationship("ExchangeRate", backref="alerts")
    prediction = relationship("Prediction", backref="alerts")
    
    # インデックス
    __table_args__ = (
        Index('idx_active_alerts_setting_created', 'alert_setting_id', 'created_at'),
        Index('idx_active_alerts_severity', 'severity'),
        Index('idx_active_alerts_acknowledged', 'is_acknowledged'),
    )

# ===================================================================
# 予測設定モデル
# ===================================================================

class PredictionSetting(Base):
    """
    予測設定テーブル
    
    機械学習モデルのパラメーターとアンサンブル設定を管理。
    LSTM・XGBoostの重み調整と感度設定を含む。
    """
    __tablename__ = "prediction_settings"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False, default='default')
    
    # モデル設定
    is_active = Column(Boolean, default=True)
    model_weights = Column(Text, nullable=False)            # JSON形式のモデル重み
    
    # LSTM設定
    lstm_enabled = Column(Boolean, default=True)
    lstm_sequence_length = Column(Integer, default=60)      # 入力系列長
    lstm_layers = Column(Integer, default=2)                # LSTM層数
    lstm_units = Column(Integer, default=50)                # ユニット数
    
    # XGBoost設定
    xgboost_enabled = Column(Boolean, default=True)
    xgboost_n_estimators = Column(Integer, default=100)     # 推定器数
    xgboost_max_depth = Column(Integer, default=6)          # 最大深度
    xgboost_learning_rate = Column(DECIMAL(5, 4), default=0.1) # 学習率
    
    # アンサンブル設定
    ensemble_method = Column(String(50), default='weighted_average') # 統合方法
    confidence_threshold = Column(DECIMAL(5, 4), default=0.7) # 信頼度閾値
    
    # 予測感度
    sensitivity_mode = Column(String(20), default='standard') # conservative, standard, aggressive
    volatility_adjustment = Column(Boolean, default=True)    # ボラティリティ調整
    
    # タイムスタンプ
    created_at = Column(DateTime, default=func.now(), nullable=False)
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now(), nullable=False)
    
    # インデックス
    __table_args__ = (
        Index('idx_prediction_settings_active', 'is_active'),
        CheckConstraint('lstm_sequence_length > 0', name='check_lstm_sequence_positive'),
        CheckConstraint('xgboost_n_estimators > 0', name='check_xgboost_estimators_positive'),
        CheckConstraint('confidence_threshold >= 0 AND confidence_threshold <= 1', name='check_confidence_threshold_range'),
        UniqueConstraint('name', name='unique_prediction_setting_name'),
    )

# ===================================================================
# データ品質管理モデル
# ===================================================================

class DataQuality(Base):
    """
    データ品質監視テーブル
    
    データ収集の品質指標と異常検知結果を記録。
    欠損値・外れ値・整合性チェックの結果を追跡。
    """
    __tablename__ = "data_quality"
    
    id = Column(Integer, primary_key=True, index=True)
    check_date = Column(Date, nullable=False, index=True)
    
    # 品質指標
    total_records = Column(Integer, nullable=False)
    missing_records = Column(Integer, default=0)
    interpolated_records = Column(Integer, default=0)
    outlier_records = Column(Integer, default=0)
    
    # データ完整性
    completeness_rate = Column(DECIMAL(5, 4), nullable=False) # 完全性率
    accuracy_rate = Column(DECIMAL(5, 4), nullable=False)    # 正確性率
    consistency_rate = Column(DECIMAL(5, 4), nullable=False) # 整合性率
    
    # 期間統計
    date_range_start = Column(Date, nullable=False)
    date_range_end = Column(Date, nullable=False)
    business_days_expected = Column(Integer, nullable=False)
    business_days_actual = Column(Integer, nullable=False)
    
    # 詳細情報
    quality_issues = Column(Text, nullable=True)            # JSON形式の問題詳細
    repair_log = Column(Text, nullable=True)                # JSON形式の修復履歴
    
    # データソース別品質
    source_quality_scores = Column(Text, nullable=True)     # JSON形式のソース別スコア
    
    # タイムスタンプ
    created_at = Column(DateTime, default=func.now(), nullable=False)
    
    # インデックス
    __table_args__ = (
        Index('idx_data_quality_date_range', 'date_range_start', 'date_range_end'),
        CheckConstraint('completeness_rate >= 0 AND completeness_rate <= 1', name='check_completeness_rate_range'),
        CheckConstraint('accuracy_rate >= 0 AND accuracy_rate <= 1', name='check_accuracy_rate_range'),
        CheckConstraint('consistency_rate >= 0 AND consistency_rate <= 1', name='check_consistency_rate_range'),
        CheckConstraint('date_range_end >= date_range_start', name='check_date_range_order'),
        UniqueConstraint('check_date', name='unique_quality_check_per_date'),
    )

# ===================================================================
# テクニカル指標モデル
# ===================================================================

class TechnicalIndicator(Base):
    """
    テクニカル指標テーブル
    
    移動平均・RSI・MACD・ボリンジャーバンド等のテクニカル分析指標を格納。
    予測モデルの特徴量として活用される。
    """
    __tablename__ = "technical_indicators"
    
    id = Column(Integer, primary_key=True, index=True)
    date = Column(Date, nullable=False, index=True)
    exchange_rate_id = Column(Integer, ForeignKey('exchange_rates.id'), nullable=False)
    
    # 移動平均
    sma_5 = Column(DECIMAL(10, 4), nullable=True)          # 5日単純移動平均
    sma_25 = Column(DECIMAL(10, 4), nullable=True)         # 25日単純移動平均
    sma_75 = Column(DECIMAL(10, 4), nullable=True)         # 75日単純移動平均
    ema_12 = Column(DECIMAL(10, 4), nullable=True)         # 12日指数移動平均
    ema_26 = Column(DECIMAL(10, 4), nullable=True)         # 26日指数移動平均
    
    # オシレーター系
    rsi_14 = Column(DECIMAL(6, 4), nullable=True)          # RSI (14日)
    stochastic_k = Column(DECIMAL(6, 4), nullable=True)    # ストキャスティクス %K
    stochastic_d = Column(DECIMAL(6, 4), nullable=True)    # ストキャスティクス %D
    
    # MACD
    macd = Column(DECIMAL(10, 6), nullable=True)           # MACD線
    macd_signal = Column(DECIMAL(10, 6), nullable=True)    # シグナル線
    macd_histogram = Column(DECIMAL(10, 6), nullable=True) # ヒストグラム
    
    # ボリンジャーバンド
    bb_upper = Column(DECIMAL(10, 4), nullable=True)       # 上部バンド
    bb_middle = Column(DECIMAL(10, 4), nullable=True)      # 中央線（SMA20）
    bb_lower = Column(DECIMAL(10, 4), nullable=True)       # 下部バンド
    bb_width = Column(DECIMAL(10, 6), nullable=True)       # バンド幅
    
    # ボラティリティ系
    atr_14 = Column(DECIMAL(10, 4), nullable=True)         # ATR (14日)
    volatility_20 = Column(DECIMAL(10, 6), nullable=True)  # 20日ボラティリティ
    
    # タイムスタンプ
    created_at = Column(DateTime, default=func.now(), nullable=False)
    
    # リレーション
    exchange_rate = relationship("ExchangeRate", backref="technical_indicators")
    
    # インデックス
    __table_args__ = (
        Index('idx_technical_indicators_date_rate', 'date', 'exchange_rate_id'),
        UniqueConstraint('date', 'exchange_rate_id', name='unique_technical_per_date_rate'),
    )

# ===================================================================
# ユーザー認証モデル
# ===================================================================

class User(Base):
    """
    ユーザーテーブル
    
    JWT認証によるユーザー管理。管理者と一般ユーザーの役割分離。
    パスワードはbcryptでハッシュ化して保存。
    """
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, nullable=False, index=True)
    email = Column(String(255), unique=True, nullable=False, index=True)
    hashed_password = Column(String(255), nullable=False)
    
    # ユーザー情報
    full_name = Column(String(100), nullable=True)
    role = Column(Enum(UserRole), nullable=False, default=UserRole.USER)
    
    # アカウント状態
    is_active = Column(Boolean, default=True, nullable=False)
    is_verified = Column(Boolean, default=False, nullable=False)
    
    # セキュリティ
    failed_login_attempts = Column(Integer, default=0, nullable=False)
    last_login_at = Column(DateTime, nullable=True)
    last_failed_login_at = Column(DateTime, nullable=True)
    password_changed_at = Column(DateTime, default=func.now(), nullable=False)
    
    # タイムスタンプ
    created_at = Column(DateTime, default=func.now(), nullable=False)
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now(), nullable=False)
    
    # インデックス
    __table_args__ = (
        Index('idx_users_email_active', 'email', 'is_active'),
        Index('idx_users_username_active', 'username', 'is_active'),
        Index('idx_users_role', 'role'),
        CheckConstraint('failed_login_attempts >= 0', name='check_failed_attempts_non_negative'),
        CheckConstraint('length(username) >= 3', name='check_username_min_length'),
        CheckConstraint('length(email) >= 5', name='check_email_min_length'),
    )

# ===================================================================
# システム設定モデル
# ===================================================================

class SystemSetting(Base):
    """
    システム設定テーブル
    
    全体システムの動作パラメーターとメンテナンス設定を管理。
    シングルトンパターンで常に1レコードのみ存在。
    """
    __tablename__ = "system_settings"
    
    id = Column(Integer, primary_key=True, index=True)
    
    # データ収集設定
    auto_data_collection_enabled = Column(Boolean, default=True)
    data_collection_time = Column(String(10), default='06:00')  # 収集時刻（HH:MM）
    max_retry_attempts = Column(Integer, default=3)
    
    # 予測実行設定
    auto_prediction_enabled = Column(Boolean, default=True)
    prediction_time = Column(String(10), default='07:00')       # 予測実行時刻
    prediction_history_days = Column(Integer, default=1095)     # 予測履歴保持日数（3年）
    
    # データ保持設定
    exchange_rate_retention_years = Column(Integer, default=50)  # 為替データ保持年数
    backtest_retention_months = Column(Integer, default=12)     # バックテスト結果保持月数
    alert_retention_days = Column(Integer, default=90)         # アラート履歴保持日数
    
    # システム監視
    health_check_interval_minutes = Column(Integer, default=5)  # ヘルスチェック間隔
    data_quality_check_enabled = Column(Boolean, default=True)
    
    # 外部API設定
    alpha_vantage_daily_limit = Column(Integer, default=500)    # Alpha Vantage日次制限
    request_timeout_seconds = Column(Integer, default=30)      # リクエストタイムアウト
    
    # メンテナンス
    maintenance_mode = Column(Boolean, default=False)
    maintenance_message = Column(Text, nullable=True)
    
    # タイムスタンプ
    created_at = Column(DateTime, default=func.now(), nullable=False)
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now(), nullable=False)
    
    # インデックス
    __table_args__ = (
        CheckConstraint('max_retry_attempts > 0', name='check_max_retry_positive'),
        CheckConstraint('exchange_rate_retention_years > 0', name='check_retention_years_positive'),
        CheckConstraint('health_check_interval_minutes > 0', name='check_health_check_interval_positive'),
    )

# ===================================================================
# データベース初期化用のメタデータとヘルパー関数
# ===================================================================

def get_all_models():
    """
    すべてのモデルクラスを返すヘルパー関数
    マイグレーション時にAlembicが参照する
    """
    return [
        User,
        ExchangeRate,
        Prediction,
        TradingSignal,
        BacktestResult,
        DataSource,
        AlertSetting,
        ActiveAlert,
        PredictionSetting,
        DataQuality,
        TechnicalIndicator,
        SystemSetting,
    ]

# ===================================================================
# モデル設計要約
# ===================================================================

"""
データベース設計要約:
==================

1. 為替レートデータ（ExchangeRate）
   - 1990年からの日次OHLC データ
   - 複数ソース対応、品質管理フラグ付き

2. 予測システム（Prediction + TradingSignal）
   - 1週間〜1ヶ月の期間別予測
   - 信頼区間とボラティリティ付き
   - 5段階売買シグナル

3. バックテスト（BacktestResult）
   - 包括的なパフォーマンス分析
   - リスク調整済み指標

4. データ品質管理（DataQuality + DataSource）
   - 自動監視と修復機能
   - 複数ソースの統合管理

5. 設定・アラート（PredictionSetting + AlertSetting）
   - 柔軟なモデルパラメーター調整
   - カスタマイズ可能な通知システム

6. テクニカル分析（TechnicalIndicator）
   - 主要指標の自動計算
   - 予測モデルの特徴量

設計原則:
- PostgreSQL 15+ 最適化
- 完全正規化（3NF）
- 包括的インデックス戦略
- 制約による品質保証
- 論理削除未使用（予測システムでは履歴保持が重要）
"""