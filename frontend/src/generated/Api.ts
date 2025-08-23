/* eslint-disable */
/* tslint:disable */
// @ts-nocheck
/*
 * ---------------------------------------------------------------
 * ## THIS FILE WAS GENERATED VIA SWAGGER-TYPESCRIPT-API        ##
 * ##                                                           ##
 * ## AUTHOR: acacode                                           ##
 * ## SOURCE: https://github.com/acacode/swagger-typescript-api ##
 * ---------------------------------------------------------------
 */

/** SignalType */
export enum SignalType {
  StrongSell = "strong_sell",
  Sell = "sell",
  Hold = "hold",
  Buy = "buy",
  StrongBuy = "strong_buy",
}

/**
 * PredictionPeriod
 * 予測期間の列挙
 */
export enum PredictionPeriod {
  Value1Week = "1week",
  Value2Weeks = "2weeks",
  Value3Weeks = "3weeks",
  Value1Month = "1month",
}

/** PredictionModelType */
export enum PredictionModelType {
  Lstm = "lstm",
  Xgboost = "xgboost",
  Ensemble = "ensemble",
}

/**
 * PredictionModel
 * 予測モデルタイプの列挙
 */
export enum PredictionModel {
  Lstm = "lstm",
  Xgboost = "xgboost",
  Ensemble = "ensemble",
}

/**
 * DataSourceType
 * データソース種別
 */
export enum DataSourceType {
  BojCsv = "boj_csv",
  YahooFinance = "yahoo_finance",
  AlphaVantage = "alpha_vantage",
  Scraping = "scraping",
}

/**
 * DataSourceStatus
 * データソース状態
 */
export enum DataSourceStatus {
  Active = "active",
  Inactive = "inactive",
  Error = "error",
  Maintenance = "maintenance",
}

/** BacktestStatusType */
export enum BacktestStatusType {
  Pending = "pending",
  Running = "running",
  Completed = "completed",
  Failed = "failed",
}

/**
 * BacktestConfig
 * バックテスト設定リクエスト
 */
export interface BacktestConfig {
  /**
   * Start Date
   * バックテスト開始日
   * @format date
   */
  start_date: string;
  /**
   * End Date
   * バックテスト終了日
   * @format date
   */
  end_date: string;
  /**
   * Initial Capital
   * 初期資金（円）
   * @default "1000000"
   */
  initial_capital?: number | string;
  /**
   * 使用する予測モデル
   * @default "ensemble"
   */
  prediction_model_type?: PredictionModelType;
  /**
   * Prediction Model Config
   * モデル固有設定（JSON形式）
   */
  prediction_model_config?: object | null;
}

/**
 * BacktestJobResponse
 * バックテスト実行レスポンス
 */
export interface BacktestJobResponse {
  /**
   * Job Id
   * ジョブID
   */
  job_id: string;
  /** 実行状態 */
  status: BacktestStatusType;
  /**
   * Start Date
   * バックテスト開始日
   * @format date
   */
  start_date: string;
  /**
   * End Date
   * バックテスト終了日
   * @format date
   */
  end_date: string;
  /**
   * Created At
   * 作成日時
   * @format date-time
   */
  created_at: string;
  /**
   * Estimated Completion Time
   * 推定完了時間（秒）
   */
  estimated_completion_time?: number | null;
}

/**
 * BacktestMetricsResponse
 * バックテスト評価指標レスポンス
 */
export interface BacktestMetricsResponse {
  /**
   * Job Id
   * ジョブID
   */
  job_id: string;
  /**
   * Total Return
   * 総リターン
   */
  total_return: string;
  /**
   * Annualized Return
   * 年率リターン
   */
  annualized_return: string;
  /**
   * Volatility
   * ボラティリティ
   */
  volatility: string;
  /**
   * Sharpe Ratio
   * シャープレシオ
   */
  sharpe_ratio: string;
  /**
   * Max Drawdown
   * 最大ドローダウン
   */
  max_drawdown: string;
  /**
   * Total Trades
   * 総取引数
   */
  total_trades: number;
  /**
   * Winning Trades
   * 勝ちトレード数
   */
  winning_trades: number;
  /**
   * Losing Trades
   * 負けトレード数
   */
  losing_trades: number;
  /**
   * Win Rate
   * 勝率
   */
  win_rate: string;
  /**
   * Prediction Accuracy 1W
   * 1週間予測精度
   */
  prediction_accuracy_1w?: string | null;
  /**
   * Prediction Accuracy 2W
   * 2週間予測精度
   */
  prediction_accuracy_2w?: string | null;
  /**
   * Prediction Accuracy 3W
   * 3週間予測精度
   */
  prediction_accuracy_3w?: string | null;
  /**
   * Prediction Accuracy 1M
   * 1ヶ月予測精度
   */
  prediction_accuracy_1m?: string | null;
  /**
   * Sortino Ratio
   * ソルティノレシオ
   */
  sortino_ratio?: string | null;
  /**
   * Calmar Ratio
   * カルマーレシオ
   */
  calmar_ratio?: string | null;
  /**
   * Var 95
   * VaR（95%）
   */
  var_95?: string | null;
  /**
   * Monthly Returns
   * 月次リターン
   */
  monthly_returns?: string[] | null;
  /**
   * Rolling Sharpe
   * ローリングシャープレシオ
   */
  rolling_sharpe?: string[] | null;
}

/**
 * BacktestResultsResponse
 * バックテスト結果レスポンス
 */
export interface BacktestResultsResponse {
  /**
   * Job Id
   * ジョブID
   */
  job_id: string;
  /** 実行状態 */
  status: BacktestStatusType;
  /**
   * Start Date
   * バックテスト開始日
   * @format date
   */
  start_date: string;
  /**
   * End Date
   * バックテスト終了日
   * @format date
   */
  end_date: string;
  /**
   * Initial Capital
   * 初期資金
   */
  initial_capital: string;
  /** 使用モデル */
  prediction_model_type: PredictionModelType;
  /**
   * Execution Time
   * 実行時間（秒）
   */
  execution_time?: number | null;
  /**
   * Completed At
   * 完了日時
   */
  completed_at?: string | null;
  /**
   * Error Message
   * エラーメッセージ
   */
  error_message?: string | null;
  /**
   * Total Return
   * 総リターン
   */
  total_return?: string | null;
  /**
   * Annualized Return
   * 年率リターン
   */
  annualized_return?: string | null;
  /**
   * Volatility
   * ボラティリティ
   */
  volatility?: string | null;
  /**
   * Sharpe Ratio
   * シャープレシオ
   */
  sharpe_ratio?: string | null;
  /**
   * Max Drawdown
   * 最大ドローダウン
   */
  max_drawdown?: string | null;
  /**
   * Total Trades
   * 総取引数
   */
  total_trades?: number | null;
  /**
   * Winning Trades
   * 勝ちトレード数
   */
  winning_trades?: number | null;
  /**
   * Losing Trades
   * 負けトレード数
   */
  losing_trades?: number | null;
  /**
   * Win Rate
   * 勝率
   */
  win_rate?: string | null;
}

/**
 * BacktestTradesResponse
 * バックテスト取引履歴レスポンス
 */
export interface BacktestTradesResponse {
  /**
   * Job Id
   * ジョブID
   */
  job_id: string;
  /**
   * Total Trades
   * 総取引数
   */
  total_trades: number;
  /**
   * Page
   * ページ番号
   * @default 1
   */
  page?: number;
  /**
   * Page Size
   * ページサイズ
   * @default 100
   */
  page_size?: number;
  /**
   * Total Pages
   * 総ページ数
   */
  total_pages: number;
  /**
   * Trades
   * 取引記録
   */
  trades: TradeRecord[];
  /**
   * Profit Trades
   * 利益取引数
   */
  profit_trades: number;
  /**
   * Loss Trades
   * 損失取引数
   */
  loss_trades: number;
  /**
   * Average Profit
   * 平均利益
   */
  average_profit: string;
  /**
   * Average Loss
   * 平均損失
   */
  average_loss: string;
  /**
   * Largest Profit
   * 最大利益
   */
  largest_profit: string;
  /**
   * Largest Loss
   * 最大損失
   */
  largest_loss: string;
}

/**
 * CollectionProgress
 * データ収集進捗情報
 */
export interface CollectionProgress {
  /**
   * Source Name
   * データソース名
   */
  source_name: string;
  /**
   * Total Items
   * 総アイテム数
   */
  total_items: number;
  /**
   * Completed Items
   * 完了アイテム数
   */
  completed_items: number;
  /**
   * Failed Items
   * 失敗アイテム数
   * @default 0
   */
  failed_items?: number;
  /**
   * Progress Percentage
   * 進捗率（0-100）
   */
  progress_percentage: number;
  /**
   * Estimated Remaining Minutes
   * 残り予想時間（分）
   */
  estimated_remaining_minutes?: number | null;
  /**
   * Current Activity
   * 現在の処理内容
   */
  current_activity: string;
}

/**
 * CollectionScheduleInfo
 * データ収集スケジュール情報
 */
export interface CollectionScheduleInfo {
  /**
   * Auto Collection Enabled
   * 自動収集有効/無効
   * @example true
   */
  auto_collection_enabled: boolean;
  /**
   * Next Collection Time
   * 次回収集予定時刻
   * @format date-time
   */
  next_collection_time: string;
  /**
   * Collection Frequency
   * 収集頻度
   * @example "daily"
   */
  collection_frequency: string;
  /**
   * Last Successful Collection
   * 最終成功収集日時
   */
  last_successful_collection?: string | null;
  /**
   * Last Failed Collection
   * 最終失敗収集日時
   */
  last_failed_collection?: string | null;
  /**
   * Consecutive Failures
   * 連続失敗回数
   * @default 0
   */
  consecutive_failures?: number;
}

/**
 * CurrentRateResponse
 * 現在レート取得レスポンス
 */
export interface CurrentRateResponse {
  /** Rate */
  rate: number;
  /**
   * Timestamp
   * @format date-time
   */
  timestamp: string;
  /** Change 24H */
  change_24h: number;
  /** Change Percentage 24H */
  change_percentage_24h: number;
  /** Open Rate */
  open_rate?: number | null;
  /** High Rate */
  high_rate?: number | null;
  /** Low Rate */
  low_rate?: number | null;
  /** Volume */
  volume?: number | null;
  /** Is Market Open */
  is_market_open: boolean;
  /** Source */
  source: string;
}

/**
 * CurrentSignalResponse
 * 現在の売買シグナル取得APIレスポンス
 */
export interface CurrentSignalResponse {
  /** 売買シグナルレスポンスモデル */
  signal: TradingSignalResponse;
  /** 前回シグナル */
  previous_signal?: SignalType | null;
  /**
   * Signal Changed
   * シグナル変化フラグ
   * @default false
   */
  signal_changed?: boolean;
  /**
   * Display Text
   * シグナル表示テキスト
   */
  display_text: string;
  /**
   * Color Code
   * UIカラーコード
   */
  color_code: string;
  /**
   * Trend Arrow
   * トレンド矢印表示
   */
  trend_arrow: string;
  /**
   * Last Updated
   * 最終更新時刻
   * @format date-time
   */
  last_updated: string;
  /**
   * Next Update At
   * 次回更新予定時刻
   */
  next_update_at?: string | null;
}

/**
 * DataCollectionRequest
 * データ収集実行リクエスト
 */
export interface DataCollectionRequest {
  /**
   * Sources
   * 収集対象データソース（空の場合は全て）
   */
  sources?: DataSourceType[] | null;
  /**
   * Force Update
   * 強制更新フラグ
   * @default false
   */
  force_update?: boolean;
  /**
   * Date Range
   * 収集日付範囲 {start: 'YYYY-MM-DD', end: 'YYYY-MM-DD'}
   */
  date_range?: Record<string, string> | null;
  /**
   * Notify On Completion
   * 完了通知有無
   * @default true
   */
  notify_on_completion?: boolean;
}

/**
 * DataCollectionResponse
 * データ収集実行レスポンス
 */
export interface DataCollectionResponse {
  /**
   * Collection Id
   * 収集ジョブID
   */
  collection_id: string;
  /**
   * Status
   * 収集状態
   * @example "started"
   */
  status: string;
  /**
   * Message
   * 収集開始メッセージ
   */
  message: string;
  /**
   * Sources Count
   * 対象ソース数
   */
  sources_count: number;
  /**
   * Started At
   * 開始日時
   * @format date-time
   */
  started_at: string;
  /**
   * Estimated Completion
   * 完了予定日時
   */
  estimated_completion?: string | null;
  /**
   * Progress
   * 各ソース進捗
   * @default []
   */
  progress?: CollectionProgress[];
}

/**
 * DataCoverageInfo
 * データカバレッジ情報
 */
export interface DataCoverageInfo {
  /**
   * Total Expected Days
   * 期待される総営業日数
   * @example 8750
   */
  total_expected_days: number;
  /**
   * Actual Data Days
   * 実際のデータ日数
   * @example 8720
   */
  actual_data_days: number;
  /**
   * Missing Days
   * 欠損日数
   * @example 30
   */
  missing_days: number;
  /**
   * Coverage Rate
   * カバレッジ率（0-1）
   * @example 0.996
   */
  coverage_rate: number;
  /**
   * Interpolated Days
   * 補間データ日数
   * @example 15
   */
  interpolated_days: number;
  /**
   * Earliest Date
   * 最古データ日付
   * @format date
   * @example "1990-01-01"
   */
  earliest_date: string;
  /**
   * Latest Date
   * 最新データ日付
   * @format date
   * @example "2024-08-22"
   */
  latest_date: string;
  /**
   * Last Update
   * 最終更新日時
   * @format date-time
   */
  last_update: string;
}

/**
 * DataQualityMetrics
 * データ品質指標
 */
export interface DataQualityMetrics {
  /**
   * Completeness Rate
   * 完全性率（0-1）
   * @example 0.996
   */
  completeness_rate: number;
  /**
   * Accuracy Rate
   * 正確性率（0-1）
   * @example 0.999
   */
  accuracy_rate: number;
  /**
   * Consistency Rate
   * 整合性率（0-1）
   * @example 0.998
   */
  consistency_rate: number;
  /**
   * Outlier Count
   * 外れ値数
   * @example 5
   */
  outlier_count: number;
  /**
   * Duplicate Count
   * 重複データ数
   * @example 0
   */
  duplicate_count: number;
  /**
   * Last Quality Check
   * 最新品質チェック日時
   * @format date-time
   */
  last_quality_check: string;
  /**
   * Quality Score
   * 総合品質スコア（0-1）
   * @example 0.997
   */
  quality_score: number;
}

/**
 * DataQualityReport
 * データ品質レポート (エンドポイント 4.3)
 */
export interface DataQualityReport {
  /**
   * Report Id
   * レポートID
   */
  report_id: string;
  /**
   * Report Date
   * レポート生成日時
   * @format date-time
   */
  report_date: string;
  /**
   * Analysis Period
   * 分析期間 {start: date, end: date}
   */
  analysis_period: Record<string, string>;
  /**
   * Overall Quality Score
   * 総合品質スコア（0-1）
   * @example 0.945
   */
  overall_quality_score: number;
  /**
   * Data Health Status
   * データヘルス状態
   * @example "good"
   */
  data_health_status: string;
  /** 詳細品質指標 */
  quality_metrics: DataQualityMetrics;
  /**
   * Source Scores
   * ソース別品質スコア
   */
  source_scores: SourceQualityScore[];
  /**
   * Quality Issues
   * 品質問題一覧
   */
  quality_issues: QualityIssue[];
  /**
   * Quality Trends
   * 品質傾向（過去比較）
   */
  quality_trends: Record<string, number>;
  /**
   * Recommendations
   * 品質改善推奨事項
   */
  recommendations: string[];
  /**
   * Next Analysis Scheduled
   * 次回分析予定日時
   * @format date-time
   */
  next_analysis_scheduled: string;
}

/**
 * DataRepairRequest
 * データ修復実行リクエスト
 */
export interface DataRepairRequest {
  /**
   * Repair Targets
   * 修復対象リスト
   */
  repair_targets: RepairTarget[];
  /**
   * Repair Strategy
   * 修復戦略
   * @default "conservative"
   */
  repair_strategy?: string;
  /**
   * Dry Run
   * テスト実行フラグ（実際の修復は行わない）
   * @default true
   */
  dry_run?: boolean;
  /**
   * Backup Before Repair
   * 修復前バックアップ作成
   * @default true
   */
  backup_before_repair?: boolean;
  /**
   * Notify On Completion
   * 完了通知有無
   * @default true
   */
  notify_on_completion?: boolean;
}

/**
 * DataRepairResponse
 * データ修復実行レスポンス (エンドポイント 4.4)
 */
export interface DataRepairResponse {
  /**
   * Repair Id
   * 修復ジョブID
   */
  repair_id: string;
  /**
   * Status
   * 修復状態
   * @example "started"
   */
  status: string;
  /**
   * Is Dry Run
   * テスト実行かどうか
   */
  is_dry_run: boolean;
  /**
   * Message
   * 修復開始メッセージ
   */
  message: string;
  /**
   * Started At
   * 開始日時
   * @format date-time
   */
  started_at: string;
  /**
   * Estimated Completion
   * 完了予定日時
   */
  estimated_completion?: string | null;
  /**
   * Targets Count
   * 修復対象数
   */
  targets_count: number;
  /**
   * Total Date Range
   * 全体対象期間
   */
  total_date_range: Record<string, string>;
  /**
   * Repair Results
   * 修復結果リスト
   * @default []
   */
  repair_results?: RepairResult[];
  /**
   * Errors
   * エラーメッセージリスト
   * @default []
   */
  errors?: string[];
  /**
   * Warnings
   * 警告メッセージリスト
   * @default []
   */
  warnings?: string[];
  /**
   * Completed At
   * 完了日時
   */
  completed_at?: string | null;
  /**
   * Total Execution Time
   * 実行時間（秒）
   */
  total_execution_time?: number | null;
}

/**
 * DataSourceHealthInfo
 * データソース健全性情報
 */
export interface DataSourceHealthInfo {
  /**
   * Total Sources
   * 総データソース数
   * @example 3
   */
  total_sources: number;
  /**
   * Active Sources
   * アクティブソース数
   * @example 2
   */
  active_sources: number;
  /**
   * Error Sources
   * エラーソース数
   * @example 1
   */
  error_sources: number;
  /**
   * Maintenance Sources
   * メンテナンス中ソース数
   * @example 0
   */
  maintenance_sources: number;
  /**
   * Overall Health
   * 全体健全性
   * @example "good"
   */
  overall_health: string;
  /**
   * Health Score
   * 健全性スコア（0-1）
   * @example 0.85
   */
  health_score: number;
  /**
   * Has Backup Sources
   * バックアップソース有無
   * @example true
   */
  has_backup_sources: boolean;
  /**
   * Primary Source Available
   * 主要ソース利用可能性
   * @example true
   */
  primary_source_available: boolean;
}

/**
 * DataSourceItem
 * データソース詳細情報
 */
export interface DataSourceItem {
  /**
   * Id
   * データソースID
   */
  id: number;
  /**
   * Name
   * データソース名
   * @example "Yahoo Finance"
   */
  name: string;
  /** ソース種別 */
  source_type: DataSourceType;
  /** 現在の状態 */
  status: DataSourceStatus;
  /**
   * Url
   * 接続URL
   */
  url?: string | null;
  /**
   * Priority
   * 優先度（1が最高）
   * @example 1
   */
  priority: number;
  /**
   * Success Rate
   * 成功率（0-1）
   * @example 0.985
   */
  success_rate: number;
  /**
   * Avg Response Time
   * 平均レスポンス時間（ms）
   * @example 1200
   */
  avg_response_time?: number | null;
  /**
   * Last Success At
   * 最終成功日時
   */
  last_success_at?: string | null;
  /**
   * Last Failure At
   * 最終失敗日時
   */
  last_failure_at?: string | null;
  /**
   * Failure Count
   * 累計失敗回数
   * @default 0
   */
  failure_count?: number;
  /**
   * Rate Limit Requests
   * リクエスト数制限/期間
   */
  rate_limit_requests?: number | null;
  /**
   * Rate Limit Period
   * 制限期間（秒）
   */
  rate_limit_period?: number | null;
  /**
   * Daily Request Count
   * 本日リクエスト数
   * @default 0
   */
  daily_request_count?: number;
  /**
   * Remaining Requests
   * 残りリクエスト数
   */
  remaining_requests?: number | null;
  /**
   * Created At
   * 作成日時
   * @format date-time
   */
  created_at: string;
  /**
   * Updated At
   * 更新日時
   * @format date-time
   */
  updated_at: string;
}

/**
 * DataSourcesResponse
 * データソース稼働状況取得レスポンス
 * エンドポイント: GET /api/data/sources
 */
export interface DataSourcesResponse {
  /**
   * Sources
   * データソース詳細一覧
   */
  sources: DataSourceItem[];
  /** 健全性情報 */
  health: DataSourceHealthInfo;
  /**
   * Last Health Check
   * 最終ヘルスチェック日時
   * @format date-time
   */
  last_health_check: string;
  /**
   * Next Health Check
   * 次回ヘルスチェック予定日時
   * @format date-time
   */
  next_health_check: string;
  /**
   * Recommendations
   * システム推奨事項
   * @default []
   */
  recommendations?: string[];
  /**
   * Response Generated At
   * レスポンス生成日時
   * @format date-time
   */
  response_generated_at: string;
}

/**
 * DataStatusResponse
 * データ収集状況取得レスポンス
 * エンドポイント: GET /api/data/status
 */
export interface DataStatusResponse {
  /** データカバレッジ情報 */
  coverage: DataCoverageInfo;
  /** データ品質指標 */
  quality: DataQualityMetrics;
  /** 収集スケジュール情報 */
  schedule: CollectionScheduleInfo;
  /**
   * System Health
   * システム健全性
   * @example "healthy"
   */
  system_health: string;
  /**
   * Active Issues
   * アクティブな問題一覧
   * @default []
   */
  active_issues?: string[];
  /**
   * Status Generated At
   * ステータス生成日時
   * @format date-time
   */
  status_generated_at: string;
}

/**
 * DetailedPredictionItem
 * 詳細予測項目
 */
export interface DetailedPredictionItem {
  /** 予測期間 */
  period: PredictionPeriod;
  /**
   * Predicted Rate
   * 最終予測レート
   * @exclusiveMin 0
   */
  predicted_rate: number;
  /**
   * Confidence Interval Lower
   * 信頼区間下限
   */
  confidence_interval_lower?: number | null;
  /**
   * Confidence Interval Upper
   * 信頼区間上限
   */
  confidence_interval_upper?: number | null;
  /**
   * Volatility
   * 予測ボラティリティ
   */
  volatility?: number | null;
  /**
   * Prediction Strength
   * 予測強度
   * @min 0
   * @max 1
   * @default 0.5
   */
  prediction_strength?: number;
  /**
   * Target Date
   * 予測対象日
   * @format date
   */
  target_date: string;
  /**
   * Model Analyses
   * モデル別分析
   */
  model_analyses: ModelAnalysis[];
  /**
   * Uncertainty Factors
   * 不確実性要因
   */
  uncertainty_factors?: string[];
  /**
   * Risk Assessment
   * リスク評価（low/medium/high/critical）
   * @default "medium"
   */
  risk_assessment?: string;
  /**
   * Scenario Analysis
   * シナリオ分析（楽観/悲観/現実的）
   */
  scenario_analysis?: Record<string, number> | null;
}

/**
 * DetailedPredictionsResponse
 * 詳細予測分析レスポンス
 */
export interface DetailedPredictionsResponse {
  /**
   * Predictions
   * 詳細予測データ
   */
  predictions: DetailedPredictionItem[];
  /**
   * Prediction Date
   * 予測実行日
   * @format date
   */
  prediction_date: string;
  /**
   * Current Rate
   * 現在レート
   * @exclusiveMin 0
   */
  current_rate: number;
  /** 市場環境分析 */
  market_condition: MarketCondition;
  /**
   * Model Version
   * 使用モデルバージョン
   */
  model_version: string;
  /**
   * Data Quality Score
   * データ品質スコア
   * @min 0
   * @max 1
   * @default 1
   */
  data_quality_score?: number;
  /**
   * Prediction Horizon Days
   * 期間別予測日数
   */
  prediction_horizon_days: Record<string, number>;
  /**
   * Generated At
   * 生成日時
   * @format date-time
   */
  generated_at: string;
  /**
   * Processing Time Seconds
   * 処理時間（秒）
   */
  processing_time_seconds?: number | null;
  /**
   * Data Points Used
   * 使用データポイント数
   */
  data_points_used?: number | null;
}

/**
 * FeatureImportance
 * 特徴量重要度
 */
export interface FeatureImportance {
  /**
   * Feature Name
   * 特徴量名
   */
  feature_name: string;
  /**
   * Importance Score
   * 重要度スコア
   * @min 0
   * @max 1
   */
  importance_score: number;
  /**
   * Category
   * カテゴリ（technical/economic/temporal等）
   */
  category: string;
}

/** HTTPValidationError */
export interface HTTPValidationError {
  /** Detail */
  detail?: ValidationError[];
}

/**
 * LatestPredictionsResponse
 * 最新予測レスポンス
 */
export interface LatestPredictionsResponse {
  /**
   * Predictions
   * 予測データ一覧
   */
  predictions: PredictionItem[];
  /**
   * Prediction Date
   * 予測実行日
   * @format date
   */
  prediction_date: string;
  /**
   * Confidence Level
   * 全体信頼水準
   * @min 0
   * @max 1
   * @default 0.95
   */
  confidence_level?: number;
  /**
   * Generated At
   * 生成日時
   * @format date-time
   */
  generated_at: string;
  /**
   * Model Version
   * 使用モデルバージョン
   */
  model_version: string;
}

/**
 * MarketCondition
 * 市場環境分析
 */
export interface MarketCondition {
  /**
   * Trend Direction
   * トレンド方向（upward/downward/sideways）
   */
  trend_direction: string;
  /**
   * Trend Strength
   * トレンド強度
   * @min 0
   * @max 1
   */
  trend_strength: number;
  /**
   * Volatility Regime
   * ボラティリティ環境（low/normal/high/extreme）
   */
  volatility_regime: string;
  /**
   * Market Sentiment
   * 市場センチメント（bearish/neutral/bullish）
   */
  market_sentiment: string;
  /**
   * Liquidity Condition
   * 流動性環境（tight/normal/abundant）
   */
  liquidity_condition: string;
}

/**
 * ModelAnalysis
 * モデル分析情報
 */
export interface ModelAnalysis {
  /** モデルタイプ */
  model_type: PredictionModel;
  /**
   * Weight
   * アンサンブル重み
   * @min 0
   * @max 1
   */
  weight: number;
  /**
   * Individual Prediction
   * 個別予測値
   * @exclusiveMin 0
   */
  individual_prediction: number;
  /**
   * Confidence Score
   * 信頼度スコア
   * @min 0
   * @max 1
   */
  confidence_score: number;
  /**
   * Feature Importance
   * 特徴量重要度
   */
  feature_importance?: FeatureImportance[];
}

/**
 * PredictionItem
 * 個別の予測項目
 */
export interface PredictionItem {
  /** 予測期間 */
  period: PredictionPeriod;
  /**
   * Predicted Rate
   * 予測レート
   * @exclusiveMin 0
   */
  predicted_rate: number;
  /**
   * Confidence Interval Lower
   * 信頼区間下限
   */
  confidence_interval_lower?: number | null;
  /**
   * Confidence Interval Upper
   * 信頼区間上限
   */
  confidence_interval_upper?: number | null;
  /**
   * Confidence Level
   * 信頼水準
   * @min 0
   * @max 1
   * @default 0.95
   */
  confidence_level?: number;
  /**
   * Volatility
   * ボラティリティ
   */
  volatility?: number | null;
  /**
   * Prediction Strength
   * 予測強度
   * @min 0
   * @max 1
   * @default 0.5
   */
  prediction_strength?: number;
  /**
   * Target Date
   * 予測対象日
   * @format date
   */
  target_date: string;
}

/**
 * QualityIssue
 * 品質問題詳細
 */
export interface QualityIssue {
  /**
   * Issue Type
   * 問題タイプ
   * @example "missing_data"
   */
  issue_type: string;
  /**
   * Severity
   * 重要度
   * @example "medium"
   */
  severity: string;
  /**
   * Affected Dates
   * 影響日付リスト
   */
  affected_dates: string[];
  /**
   * Affected Count
   * 影響レコード数
   */
  affected_count: number;
  /**
   * Description
   * 問題説明
   */
  description: string;
  /**
   * Suggested Action
   * 推奨対応
   */
  suggested_action: string;
  /**
   * Is Auto Repairable
   * 自動修復可能性
   */
  is_auto_repairable: boolean;
}

/**
 * RepairAction
 * 修復アクション詳細
 */
export interface RepairAction {
  /**
   * Action Type
   * 修復アクションタイプ
   * @example "interpolate"
   */
  action_type: string;
  /**
   * Target Date
   * 対象日付
   * @format date
   */
  target_date: string;
  /**
   * Original Value
   * 元の値
   */
  original_value?: string | null;
  /**
   * Repaired Value
   * 修復後の値
   */
  repaired_value: string;
  /**
   * Confidence Score
   * 修復信頼度（0-1）
   */
  confidence_score: number;
  /**
   * Method Used
   * 使用した修復手法
   */
  method_used: string;
  /**
   * Source Data Points
   * 修復に使用したデータポイント日付
   */
  source_data_points: string[];
}

/**
 * RepairResult
 * 修復結果サマリー
 */
export interface RepairResult {
  /**
   * Target Range
   * 修復対象範囲
   */
  target_range: Record<string, string>;
  /**
   * Total Issues Found
   * 発見された問題総数
   */
  total_issues_found: number;
  /**
   * Issues Repaired
   * 修復された問題数
   */
  issues_repaired: number;
  /**
   * Issues Skipped
   * スキップされた問題数
   */
  issues_skipped: number;
  /**
   * Repair Success Rate
   * 修復成功率（0-1）
   */
  repair_success_rate: number;
  /**
   * Avg Confidence Score
   * 平均信頼度スコア
   */
  avg_confidence_score: number;
  /**
   * Repair Actions
   * 実行された修復アクション
   */
  repair_actions: RepairAction[];
}

/**
 * RepairTarget
 * 修復対象指定
 */
export interface RepairTarget {
  /**
   * Date Range
   * 修復対象日付範囲 {start: date, end: date}
   */
  date_range: Record<string, string>;
  /**
   * Issue Types
   * 修復対象問題タイプ (空の場合は全て)
   */
  issue_types?: string[] | null;
  /**
   * Sources
   * 修復対象ソース (空の場合は全て)
   */
  sources?: DataSourceType[] | null;
  /**
   * Max Interpolation Gap
   * 最大補間ギャップ日数
   * @min 1
   * @max 30
   * @default 5
   */
  max_interpolation_gap?: number;
}

/**
 * SourceQualityScore
 * データソース別品質スコア
 */
export interface SourceQualityScore {
  /**
   * Source Name
   * ソース名
   */
  source_name: string;
  /** ソースタイプ */
  source_type: DataSourceType;
  /**
   * Completeness Score
   * 完全性スコア（0-1）
   */
  completeness_score: number;
  /**
   * Accuracy Score
   * 正確性スコア（0-1）
   */
  accuracy_score: number;
  /**
   * Timeliness Score
   * 適時性スコア（0-1）
   */
  timeliness_score: number;
  /**
   * Overall Score
   * 総合スコア（0-1）
   */
  overall_score: number;
  /**
   * Data Points Analyzed
   * 分析データポイント数
   */
  data_points_analyzed: number;
  /**
   * Last Analysis
   * 最終分析日時
   * @format date-time
   */
  last_analysis: string;
}

/**
 * TradeRecord
 * 取引記録
 */
export interface TradeRecord {
  /**
   * Trade Date
   * 取引日
   * @format date
   */
  trade_date: string;
  /**
   * Signal Type
   * 売買シグナル
   */
  signal_type: string;
  /**
   * Entry Rate
   * エントリーレート
   */
  entry_rate: string;
  /**
   * Exit Rate
   * エグジットレート
   */
  exit_rate?: string | null;
  /**
   * Position Size
   * ポジションサイズ
   */
  position_size: string;
  /**
   * Profit Loss
   * 損益
   */
  profit_loss?: string | null;
  /**
   * Holding Period
   * 保有期間（日）
   */
  holding_period?: number | null;
  /**
   * Confidence
   * シグナル信頼度
   */
  confidence: string;
  /**
   * Market Volatility
   * 市場ボラティリティ
   */
  market_volatility?: string | null;
}

/**
 * TradingSignalResponse
 * 売買シグナルレスポンスモデル
 */
export interface TradingSignalResponse {
  /** Id */
  id: number;
  /**
   * Date
   * @format date
   */
  date: string;
  /** 売買シグナル種別 */
  signal_type: SignalType;
  /**
   * Confidence
   * シグナル信頼度（0-1）
   * @min 0
   * @max 1
   */
  confidence: number;
  /**
   * Strength
   * シグナル強度（0-1）
   * @min 0
   * @max 1
   */
  strength: number;
  /**
   * Reasoning
   * シグナル根拠（JSON形式）
   */
  reasoning?: string | null;
  /**
   * Technical Score
   * テクニカル分析スコア
   */
  technical_score?: number | null;
  /**
   * Prediction Score
   * 予測分析スコア
   */
  prediction_score?: number | null;
  /**
   * Prediction Id
   * 関連予測ID
   */
  prediction_id?: number | null;
  /**
   * Current Rate
   * 現在レート
   */
  current_rate: string;
  /**
   * Created At
   * @format date-time
   */
  created_at: string;
}

/** ValidationError */
export interface ValidationError {
  /** Location */
  loc: (string | number)[];
  /** Message */
  msg: string;
  /** Error Type */
  type: string;
}

export interface GetDataSourcesApiDataSourcesGetParams {
  /**
   * Include Inactive
   * 非アクティブソースも含める
   * @default false
   */
  include_inactive?: boolean;
}

export interface GetDataQualityReportApiDataQualityGetParams {
  /**
   * Period Days
   * 品質分析期間（日数）
   * @min 1
   * @max 90
   * @default 7
   */
  period_days?: number;
}

export interface GetDataCoverageApiDataCoverageGetParams {
  /**
   * Start Date
   * 開始日 (YYYY-MM-DD)
   */
  start_date?: string | null;
  /**
   * End Date
   * 終了日 (YYYY-MM-DD)
   */
  end_date?: string | null;
}

export interface GetBacktestTradesApiBacktestTradesJobIdGetParams {
  /**
   * Page
   * @default 1
   */
  page?: number;
  /**
   * Page Size
   * @default 100
   */
  page_size?: number;
  /** Job Id */
  jobId: string;
}

export interface GetLatestPredictionsApiPredictionsLatestGetParams {
  /**
   * Periods
   * 取得する予測期間
   */
  periods?: PredictionPeriod[] | null;
}

export interface GetDetailedPredictionsApiPredictionsDetailedGetParams {
  /**
   * Period
   * 分析対象期間
   * @default "1week"
   */
  period?: PredictionPeriod | null;
  /**
   * Include Feature Importance
   * 特徴量重要度を含める
   * @default true
   */
  include_feature_importance?: boolean;
  /**
   * Include Scenario Analysis
   * シナリオ分析を含める
   * @default true
   */
  include_scenario_analysis?: boolean;
}
