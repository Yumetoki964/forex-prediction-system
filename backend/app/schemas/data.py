"""
Forex Prediction System - Data Management API Schemas
=====================================================

データ管理関連のPydanticスキーマ定義
エンドポイント 4.1: /api/data/status (データ収集状況)
エンドポイント 4.5: /api/data/sources (データソース稼働状況)
"""

from datetime import datetime, date
from decimal import Decimal
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field
from enum import Enum


class DataSourceType(str, Enum):
    """データソース種別"""
    BOJ_CSV = "boj_csv"
    YAHOO_FINANCE = "yahoo_finance"
    ALPHA_VANTAGE = "alpha_vantage"
    SCRAPING = "scraping"


class DataSourceStatus(str, Enum):
    """データソース状態"""
    ACTIVE = "active"
    INACTIVE = "inactive"
    ERROR = "error"
    MAINTENANCE = "maintenance"


class DataCoverageInfo(BaseModel):
    """データカバレッジ情報"""
    total_expected_days: int = Field(..., description="期待される総営業日数", example=8750)
    actual_data_days: int = Field(..., description="実際のデータ日数", example=8720)
    missing_days: int = Field(..., description="欠損日数", example=30)
    coverage_rate: float = Field(..., description="カバレッジ率（0-1）", example=0.996)
    interpolated_days: int = Field(..., description="補間データ日数", example=15)
    
    # 期間情報
    earliest_date: date = Field(..., description="最古データ日付", example="1990-01-01")
    latest_date: date = Field(..., description="最新データ日付", example="2024-08-22")
    last_update: datetime = Field(..., description="最終更新日時")


class DataQualityMetrics(BaseModel):
    """データ品質指標"""
    completeness_rate: float = Field(..., description="完全性率（0-1）", example=0.996)
    accuracy_rate: float = Field(..., description="正確性率（0-1）", example=0.999)
    consistency_rate: float = Field(..., description="整合性率（0-1）", example=0.998)
    
    # 異常データ統計
    outlier_count: int = Field(..., description="外れ値数", example=5)
    duplicate_count: int = Field(..., description="重複データ数", example=0)
    
    # 最新品質チェック
    last_quality_check: datetime = Field(..., description="最新品質チェック日時")
    quality_score: float = Field(..., description="総合品質スコア（0-1）", example=0.997)


class CollectionScheduleInfo(BaseModel):
    """データ収集スケジュール情報"""
    auto_collection_enabled: bool = Field(..., description="自動収集有効/無効", example=True)
    next_collection_time: datetime = Field(..., description="次回収集予定時刻")
    collection_frequency: str = Field(..., description="収集頻度", example="daily")
    last_successful_collection: Optional[datetime] = Field(None, description="最終成功収集日時")
    last_failed_collection: Optional[datetime] = Field(None, description="最終失敗収集日時")
    consecutive_failures: int = Field(0, description="連続失敗回数")


class DataStatusResponse(BaseModel):
    """
    データ収集状況取得レスポンス
    エンドポイント: GET /api/data/status
    """
    # データカバレッジ
    coverage: DataCoverageInfo = Field(..., description="データカバレッジ情報")
    
    # データ品質
    quality: DataQualityMetrics = Field(..., description="データ品質指標")
    
    # 収集スケジュール
    schedule: CollectionScheduleInfo = Field(..., description="収集スケジュール情報")
    
    # システム状態
    system_health: str = Field(..., description="システム健全性", example="healthy")  # healthy, warning, critical
    active_issues: List[str] = Field(default=[], description="アクティブな問題一覧")
    
    # 最終更新
    status_generated_at: datetime = Field(..., description="ステータス生成日時")


class DataSourceItem(BaseModel):
    """データソース詳細情報"""
    class Config:
        from_attributes = True
    
    id: int = Field(..., description="データソースID")
    name: str = Field(..., description="データソース名", example="Yahoo Finance")
    source_type: DataSourceType = Field(..., description="ソース種別")
    status: DataSourceStatus = Field(..., description="現在の状態")
    
    # 接続設定（機密情報は除外）
    url: Optional[str] = Field(None, description="接続URL")
    priority: int = Field(..., description="優先度（1が最高）", example=1)
    
    # パフォーマンス指標
    success_rate: float = Field(..., description="成功率（0-1）", example=0.985)
    avg_response_time: Optional[int] = Field(None, description="平均レスポンス時間（ms）", example=1200)
    
    # 状態履歴
    last_success_at: Optional[datetime] = Field(None, description="最終成功日時")
    last_failure_at: Optional[datetime] = Field(None, description="最終失敗日時")
    failure_count: int = Field(0, description="累計失敗回数")
    
    # レート制限
    rate_limit_requests: Optional[int] = Field(None, description="リクエスト数制限/期間")
    rate_limit_period: Optional[int] = Field(None, description="制限期間（秒）")
    daily_request_count: int = Field(0, description="本日リクエスト数")
    remaining_requests: Optional[int] = Field(None, description="残りリクエスト数")
    
    # タイムスタンプ
    created_at: datetime = Field(..., description="作成日時")
    updated_at: datetime = Field(..., description="更新日時")


class DataSourceHealthInfo(BaseModel):
    """データソース健全性情報"""
    total_sources: int = Field(..., description="総データソース数", example=3)
    active_sources: int = Field(..., description="アクティブソース数", example=2)
    error_sources: int = Field(..., description="エラーソース数", example=1)
    maintenance_sources: int = Field(..., description="メンテナンス中ソース数", example=0)
    
    # 全体健全性
    overall_health: str = Field(..., description="全体健全性", example="good")  # excellent, good, fair, poor
    health_score: float = Field(..., description="健全性スコア（0-1）", example=0.85)
    
    # 冗長性
    has_backup_sources: bool = Field(..., description="バックアップソース有無", example=True)
    primary_source_available: bool = Field(..., description="主要ソース利用可能性", example=True)


class DataSourcesResponse(BaseModel):
    """
    データソース稼働状況取得レスポンス
    エンドポイント: GET /api/data/sources
    """
    # データソース一覧
    sources: List[DataSourceItem] = Field(..., description="データソース詳細一覧")
    
    # 健全性情報
    health: DataSourceHealthInfo = Field(..., description="健全性情報")
    
    # 最新チェック
    last_health_check: datetime = Field(..., description="最終ヘルスチェック日時")
    next_health_check: datetime = Field(..., description="次回ヘルスチェック予定日時")
    
    # システム推奨事項
    recommendations: List[str] = Field(default=[], description="システム推奨事項")
    
    # レスポンス生成時刻
    response_generated_at: datetime = Field(..., description="レスポンス生成日時")


# 共通エラーレスポンス
class DataErrorResponse(BaseModel):
    """データ関連エラーレスポンス"""
    error_code: str = Field(..., description="エラーコード", example="DATA_001")
    error_message: str = Field(..., description="エラーメッセージ")
    details: Optional[Dict[str, Any]] = Field(None, description="エラー詳細情報")
    timestamp: datetime = Field(..., description="エラー発生日時")
    suggested_action: Optional[str] = Field(None, description="推奨対応")


# ===================================================================
# データ収集実行関連スキーマ (エンドポイント 4.2)
# ===================================================================

class DataCollectionRequest(BaseModel):
    """データ収集実行リクエスト"""
    sources: Optional[List[DataSourceType]] = Field(None, description="収集対象データソース（空の場合は全て）")
    force_update: bool = Field(False, description="強制更新フラグ")
    date_range: Optional[Dict[str, str]] = Field(None, description="収集日付範囲 {start: 'YYYY-MM-DD', end: 'YYYY-MM-DD'}")
    notify_on_completion: bool = Field(True, description="完了通知有無")
    

class CollectionProgress(BaseModel):
    """データ収集進捗情報"""
    source_name: str = Field(..., description="データソース名")
    total_items: int = Field(..., description="総アイテム数")
    completed_items: int = Field(..., description="完了アイテム数")
    failed_items: int = Field(0, description="失敗アイテム数")
    progress_percentage: float = Field(..., description="進捗率（0-100）")
    estimated_remaining_minutes: Optional[int] = Field(None, description="残り予想時間（分）")
    current_activity: str = Field(..., description="現在の処理内容")
    
    
class DataCollectionResponse(BaseModel):
    """データ収集実行レスポンス"""
    collection_id: str = Field(..., description="収集ジョブID")
    status: str = Field(..., description="収集状態", example="started")  # started, in_progress, completed, failed
    message: str = Field(..., description="収集開始メッセージ")
    sources_count: int = Field(..., description="対象ソース数")
    started_at: datetime = Field(..., description="開始日時")
    estimated_completion: Optional[datetime] = Field(None, description="完了予定日時")
    progress: List[CollectionProgress] = Field(default=[], description="各ソース進捗")
    

# ===================================================================
# データ品質レポート関連スキーマ (エンドポイント 4.3)
# ===================================================================

class QualityIssue(BaseModel):
    """品質問題詳細"""
    issue_type: str = Field(..., description="問題タイプ", example="missing_data")
    severity: str = Field(..., description="重要度", example="medium")  # low, medium, high, critical
    affected_dates: List[date] = Field(..., description="影響日付リスト")
    affected_count: int = Field(..., description="影響レコード数")
    description: str = Field(..., description="問題説明")
    suggested_action: str = Field(..., description="推奨対応")
    is_auto_repairable: bool = Field(..., description="自動修復可能性")
    
    
class SourceQualityScore(BaseModel):
    """データソース別品質スコア"""
    source_name: str = Field(..., description="ソース名")
    source_type: DataSourceType = Field(..., description="ソースタイプ")
    completeness_score: float = Field(..., description="完全性スコア（0-1）")
    accuracy_score: float = Field(..., description="正確性スコア（0-1）")
    timeliness_score: float = Field(..., description="適時性スコア（0-1）")
    overall_score: float = Field(..., description="総合スコア（0-1）")
    data_points_analyzed: int = Field(..., description="分析データポイント数")
    last_analysis: datetime = Field(..., description="最終分析日時")
    
    
class DataQualityReport(BaseModel):
    """データ品質レポート (エンドポイント 4.3)"""
    report_id: str = Field(..., description="レポートID")
    report_date: datetime = Field(..., description="レポート生成日時")
    analysis_period: Dict[str, date] = Field(..., description="分析期間 {start: date, end: date}")
    
    # 全体品質指標
    overall_quality_score: float = Field(..., description="総合品質スコア（0-1）", example=0.945)
    data_health_status: str = Field(..., description="データヘルス状態", example="good")  # excellent, good, fair, poor
    
    # 詳細品質メトリクス
    quality_metrics: DataQualityMetrics = Field(..., description="詳細品質指標")
    
    # ソース別品質
    source_scores: List[SourceQualityScore] = Field(..., description="ソース別品質スコア")
    
    # 検出された問題
    quality_issues: List[QualityIssue] = Field(..., description="品質問題一覧")
    
    # 傾向分析
    quality_trends: Dict[str, float] = Field(..., description="品質傾向（過去比較）")
    
    # 推奨事項
    recommendations: List[str] = Field(..., description="品質改善推奨事項")
    
    # 次回分析予定
    next_analysis_scheduled: datetime = Field(..., description="次回分析予定日時")
    

# ===================================================================
# データ修復関連スキーマ (エンドポイント 4.4)
# ===================================================================

class RepairTarget(BaseModel):
    """修復対象指定"""
    date_range: Dict[str, date] = Field(..., description="修復対象日付範囲 {start: date, end: date}")
    issue_types: Optional[List[str]] = Field(None, description="修復対象問題タイプ (空の場合は全て)")
    sources: Optional[List[DataSourceType]] = Field(None, description="修復対象ソース (空の場合は全て)")
    max_interpolation_gap: int = Field(5, description="最大補間ギャップ日数", ge=1, le=30)
    
    
class DataRepairRequest(BaseModel):
    """データ修復実行リクエスト"""
    repair_targets: List[RepairTarget] = Field(..., description="修復対象リスト")
    repair_strategy: str = Field("conservative", description="修復戦略")  # conservative, balanced, aggressive
    dry_run: bool = Field(True, description="テスト実行フラグ（実際の修復は行わない）")
    backup_before_repair: bool = Field(True, description="修復前バックアップ作成")
    notify_on_completion: bool = Field(True, description="完了通知有無")
    
    
class RepairAction(BaseModel):
    """修復アクション詳細"""
    action_type: str = Field(..., description="修復アクションタイプ", example="interpolate")
    target_date: date = Field(..., description="対象日付")
    original_value: Optional[Decimal] = Field(None, description="元の値")
    repaired_value: Decimal = Field(..., description="修復後の値")
    confidence_score: float = Field(..., description="修復信頼度（0-1）")
    method_used: str = Field(..., description="使用した修復手法")
    source_data_points: List[date] = Field(..., description="修復に使用したデータポイント日付")
    
    
class RepairResult(BaseModel):
    """修復結果サマリー"""
    target_range: Dict[str, date] = Field(..., description="修復対象範囲")
    total_issues_found: int = Field(..., description="発見された問題総数")
    issues_repaired: int = Field(..., description="修復された問題数")
    issues_skipped: int = Field(..., description="スキップされた問題数")
    repair_success_rate: float = Field(..., description="修復成功率（0-1）")
    avg_confidence_score: float = Field(..., description="平均信頼度スコア")
    repair_actions: List[RepairAction] = Field(..., description="実行された修復アクション")
    
    
class DataRepairResponse(BaseModel):
    """データ修復実行レスポンス (エンドポイント 4.4)"""
    repair_id: str = Field(..., description="修復ジョブID")
    status: str = Field(..., description="修復状態", example="started")  # started, analyzing, repairing, completed, failed
    is_dry_run: bool = Field(..., description="テスト実行かどうか")
    message: str = Field(..., description="修復開始メッセージ")
    
    # 実行情報
    started_at: datetime = Field(..., description="開始日時")
    estimated_completion: Optional[datetime] = Field(None, description="完了予定日時")
    
    # 対象情報
    targets_count: int = Field(..., description="修復対象数")
    total_date_range: Dict[str, date] = Field(..., description="全体対象期間")
    
    # 結果（完了時に更新される）
    repair_results: List[RepairResult] = Field(default=[], description="修復結果リスト")
    
    # エラー情報
    errors: List[str] = Field(default=[], description="エラーメッセージリスト")
    warnings: List[str] = Field(default=[], description="警告メッセージリスト")
    
    # 完了時情報
    completed_at: Optional[datetime] = Field(None, description="完了日時")
    total_execution_time: Optional[int] = Field(None, description="実行時間（秒）")


# 操作結果レスポンス（将来の操作エンドポイント用）
class DataOperationResponse(BaseModel):
    """データ操作結果レスポンス"""
    operation_id: str = Field(..., description="操作ID")
    operation_type: str = Field(..., description="操作種別")
    status: str = Field(..., description="操作状態", example="started")  # started, in_progress, completed, failed
    message: str = Field(..., description="操作メッセージ")
    started_at: datetime = Field(..., description="開始日時")
    estimated_completion: Optional[datetime] = Field(None, description="完了予定日時")