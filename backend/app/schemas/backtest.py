"""
Backtest API Pydantic Schemas
============================

バックテスト機能のリクエスト/レスポンススキーマ定義
過去データを使用した予測精度検証とパフォーマンス分析のAPI契約
"""

from datetime import date, datetime
from decimal import Decimal
from typing import List, Optional, Dict, Any
from enum import Enum as PyEnum

from pydantic import BaseModel, Field, ConfigDict


# ===================================================================
# Enums
# ===================================================================

class PredictionModelType(str, PyEnum):
    LSTM = "lstm"
    XGBOOST = "xgboost"
    ENSEMBLE = "ensemble"


class BacktestStatusType(str, PyEnum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"


# ===================================================================
# Request Schemas
# ===================================================================

class BacktestConfig(BaseModel):
    """バックテスト設定リクエスト"""
    start_date: date = Field(description="バックテスト開始日")
    end_date: date = Field(description="バックテスト終了日")
    initial_capital: Decimal = Field(
        default=Decimal("1000000"),
        description="初期資金（円）"
    )
    prediction_model_type: PredictionModelType = Field(
        default=PredictionModelType.ENSEMBLE,
        description="使用する予測モデル"
    )
    prediction_model_config: Optional[Dict[str, Any]] = Field(
        default=None,
        description="モデル固有設定（JSON形式）"
    )

    model_config = ConfigDict(from_attributes=True)


# ===================================================================
# Response Schemas
# ===================================================================

class BacktestJobResponse(BaseModel):
    """バックテスト実行レスポンス"""
    job_id: str = Field(description="ジョブID")
    status: BacktestStatusType = Field(description="実行状態")
    start_date: date = Field(description="バックテスト開始日")
    end_date: date = Field(description="バックテスト終了日")
    created_at: datetime = Field(description="作成日時")
    estimated_completion_time: Optional[int] = Field(
        default=None,
        description="推定完了時間（秒）"
    )

    model_config = ConfigDict(from_attributes=True)


class BacktestResultsResponse(BaseModel):
    """バックテスト結果レスポンス"""
    job_id: str = Field(description="ジョブID")
    status: BacktestStatusType = Field(description="実行状態")
    
    # 基本情報
    start_date: date = Field(description="バックテスト開始日")
    end_date: date = Field(description="バックテスト終了日")
    initial_capital: Decimal = Field(description="初期資金")
    prediction_model_type: PredictionModelType = Field(description="使用モデル")
    
    # 実行情報
    execution_time: Optional[int] = Field(
        default=None,
        description="実行時間（秒）"
    )
    completed_at: Optional[datetime] = Field(
        default=None,
        description="完了日時"
    )
    error_message: Optional[str] = Field(
        default=None,
        description="エラーメッセージ"
    )
    
    # パフォーマンス指標（基本）
    total_return: Optional[Decimal] = Field(
        default=None,
        description="総リターン"
    )
    annualized_return: Optional[Decimal] = Field(
        default=None,
        description="年率リターン"
    )
    volatility: Optional[Decimal] = Field(
        default=None,
        description="ボラティリティ"
    )
    sharpe_ratio: Optional[Decimal] = Field(
        default=None,
        description="シャープレシオ"
    )
    max_drawdown: Optional[Decimal] = Field(
        default=None,
        description="最大ドローダウン"
    )
    
    # 取引統計（基本）
    total_trades: Optional[int] = Field(
        default=None,
        description="総取引数"
    )
    winning_trades: Optional[int] = Field(
        default=None,
        description="勝ちトレード数"
    )
    losing_trades: Optional[int] = Field(
        default=None,
        description="負けトレード数"
    )
    win_rate: Optional[Decimal] = Field(
        default=None,
        description="勝率"
    )

    model_config = ConfigDict(from_attributes=True)


class BacktestMetricsResponse(BaseModel):
    """バックテスト評価指標レスポンス"""
    job_id: str = Field(description="ジョブID")
    
    # パフォーマンス指標（詳細）
    total_return: Decimal = Field(description="総リターン")
    annualized_return: Decimal = Field(description="年率リターン")
    volatility: Decimal = Field(description="ボラティリティ")
    sharpe_ratio: Decimal = Field(description="シャープレシオ")
    max_drawdown: Decimal = Field(description="最大ドローダウン")
    
    # 取引統計（詳細）
    total_trades: int = Field(description="総取引数")
    winning_trades: int = Field(description="勝ちトレード数")
    losing_trades: int = Field(description="負けトレード数")
    win_rate: Decimal = Field(description="勝率")
    
    # 予測精度
    prediction_accuracy_1w: Optional[Decimal] = Field(
        default=None,
        description="1週間予測精度"
    )
    prediction_accuracy_2w: Optional[Decimal] = Field(
        default=None,
        description="2週間予測精度"
    )
    prediction_accuracy_3w: Optional[Decimal] = Field(
        default=None,
        description="3週間予測精度"
    )
    prediction_accuracy_1m: Optional[Decimal] = Field(
        default=None,
        description="1ヶ月予測精度"
    )
    
    # リスク指標
    sortino_ratio: Optional[Decimal] = Field(
        default=None,
        description="ソルティノレシオ"
    )
    calmar_ratio: Optional[Decimal] = Field(
        default=None,
        description="カルマーレシオ"
    )
    var_95: Optional[Decimal] = Field(
        default=None,
        description="VaR（95%）"
    )
    
    # 期間別分析
    monthly_returns: Optional[List[Decimal]] = Field(
        default=None,
        description="月次リターン"
    )
    rolling_sharpe: Optional[List[Decimal]] = Field(
        default=None,
        description="ローリングシャープレシオ"
    )

    model_config = ConfigDict(from_attributes=True)


class TradeRecord(BaseModel):
    """取引記録"""
    trade_date: date = Field(description="取引日")
    signal_type: str = Field(description="売買シグナル")
    entry_rate: Decimal = Field(description="エントリーレート")
    exit_rate: Optional[Decimal] = Field(
        default=None,
        description="エグジットレート"
    )
    position_size: Decimal = Field(description="ポジションサイズ")
    profit_loss: Optional[Decimal] = Field(
        default=None,
        description="損益"
    )
    holding_period: Optional[int] = Field(
        default=None,
        description="保有期間（日）"
    )
    confidence: Decimal = Field(description="シグナル信頼度")
    market_volatility: Optional[Decimal] = Field(
        default=None,
        description="市場ボラティリティ"
    )

    model_config = ConfigDict(from_attributes=True)


class BacktestTradesResponse(BaseModel):
    """バックテスト取引履歴レスポンス"""
    job_id: str = Field(description="ジョブID")
    total_trades: int = Field(description="総取引数")
    
    # ページング情報
    page: int = Field(default=1, description="ページ番号")
    page_size: int = Field(default=100, description="ページサイズ")
    total_pages: int = Field(description="総ページ数")
    
    # 取引履歴
    trades: List[TradeRecord] = Field(description="取引記録")
    
    # 統計サマリー
    profit_trades: int = Field(description="利益取引数")
    loss_trades: int = Field(description="損失取引数")
    average_profit: Decimal = Field(description="平均利益")
    average_loss: Decimal = Field(description="平均損失")
    largest_profit: Decimal = Field(description="最大利益")
    largest_loss: Decimal = Field(description="最大損失")

    model_config = ConfigDict(from_attributes=True)


# ===================================================================
# Error Response Schemas
# ===================================================================

class BacktestError(BaseModel):
    """バックテストエラーレスポンス"""
    error_type: str = Field(description="エラー種別")
    message: str = Field(description="エラーメッセージ")
    details: Optional[Dict[str, Any]] = Field(
        default=None,
        description="エラー詳細"
    )


# ===================================================================
# Status Response Schema
# ===================================================================

class BacktestStatusResponse(BaseModel):
    """バックテスト状況レスポンス"""
    job_id: str = Field(description="ジョブID")
    status: BacktestStatusType = Field(description="実行状態")
    progress: Optional[int] = Field(
        default=None,
        ge=0,
        le=100,
        description="進捗率（0-100%）"
    )
    current_step: Optional[str] = Field(
        default=None,
        description="現在のステップ"
    )
    estimated_remaining_time: Optional[int] = Field(
        default=None,
        description="推定残り時間（秒）"
    )
    started_at: Optional[datetime] = Field(
        default=None,
        description="開始日時"
    )
    updated_at: datetime = Field(description="最終更新日時")

    model_config = ConfigDict(from_attributes=True)