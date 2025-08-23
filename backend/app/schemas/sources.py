"""
Data Sources API Schemas

データソース管理API用のPydanticスキーマ定義
- 6.1: /api/sources/status (GET) - データソース稼働状況取得
- 6.4: /api/sources/health (GET) - ソースヘルスチェック
"""

from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, List, Dict
from datetime import datetime
from enum import Enum


class DataSourceTypeEnum(str, Enum):
    """データソース種別"""
    BOJ_CSV = "boj_csv"
    YAHOO_FINANCE = "yahoo_finance"
    ALPHA_VANTAGE = "alpha_vantage"
    SCRAPING = "scraping"


class DataSourceStatusEnum(str, Enum):
    """データソース状態"""
    ACTIVE = "active"
    INACTIVE = "inactive"
    ERROR = "error"
    MAINTENANCE = "maintenance"


class HealthStatusEnum(str, Enum):
    """ヘルスチェック状態"""
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    UNHEALTHY = "unhealthy"
    UNKNOWN = "unknown"


# レスポンス用スキーマ
class DataSourceStatusItem(BaseModel):
    """データソース状況項目"""
    model_config = ConfigDict(from_attributes=True)
    
    id: int = Field(..., description="データソースID")
    name: str = Field(..., description="データソース名")
    source_type: DataSourceTypeEnum = Field(..., description="ソース種別")
    status: DataSourceStatusEnum = Field(..., description="稼働状況")
    priority: int = Field(..., description="優先度（1が最高）", ge=1)
    success_rate: float = Field(..., description="成功率", ge=0.0, le=1.0)
    avg_response_time: Optional[int] = Field(None, description="平均レスポンス時間(ms)")
    last_success_at: Optional[datetime] = Field(None, description="最終成功日時")
    last_failure_at: Optional[datetime] = Field(None, description="最終失敗日時")
    failure_count: int = Field(..., description="失敗回数", ge=0)
    daily_request_count: int = Field(..., description="日次リクエスト数", ge=0)
    rate_limit_requests: Optional[int] = Field(None, description="リクエスト制限数")
    rate_limit_period: Optional[int] = Field(None, description="制限期間(秒)")
    last_request_at: Optional[datetime] = Field(None, description="最終リクエスト日時")
    updated_at: datetime = Field(..., description="更新日時")


class DataSourcesSummary(BaseModel):
    """データソース概要統計"""
    total_sources: int = Field(..., description="総ソース数", ge=0)
    active_sources: int = Field(..., description="稼働中ソース数", ge=0)
    inactive_sources: int = Field(..., description="停止中ソース数", ge=0)
    error_sources: int = Field(..., description="エラー中ソース数", ge=0)
    maintenance_sources: int = Field(..., description="メンテナンス中ソース数", ge=0)
    average_success_rate: float = Field(..., description="全体平均成功率", ge=0.0, le=1.0)
    last_updated: datetime = Field(..., description="最終更新日時")


class SourcesStatusResponse(BaseModel):
    """データソース稼働状況レスポンス (6.1)"""
    summary: DataSourcesSummary = Field(..., description="概要統計")
    sources: List[DataSourceStatusItem] = Field(..., description="各ソース詳細")
    timestamp: datetime = Field(default_factory=datetime.now, description="取得日時")


# ヘルスチェック用スキーマ
class SourceHealthItem(BaseModel):
    """ソースヘルスチェック項目"""
    id: int = Field(..., description="データソースID")
    name: str = Field(..., description="データソース名")
    source_type: DataSourceTypeEnum = Field(..., description="ソース種別")
    health_status: HealthStatusEnum = Field(..., description="ヘルス状態")
    response_time_ms: Optional[int] = Field(None, description="レスポンス時間(ms)")
    last_check_at: datetime = Field(..., description="最終チェック日時")
    error_message: Optional[str] = Field(None, description="エラーメッセージ")
    connectivity: bool = Field(..., description="接続可能性")
    data_availability: bool = Field(..., description="データ取得可能性")
    rate_limit_status: Optional[Dict[str, int]] = Field(None, description="レート制限状況")


class HealthCheckSummary(BaseModel):
    """ヘルスチェック概要"""
    total_checked: int = Field(..., description="チェック総数", ge=0)
    healthy_count: int = Field(..., description="正常ソース数", ge=0)
    degraded_count: int = Field(..., description="性能劣化ソース数", ge=0)
    unhealthy_count: int = Field(..., description="異常ソース数", ge=0)
    unknown_count: int = Field(..., description="状態不明ソース数", ge=0)
    overall_health_score: float = Field(..., description="全体ヘルススコア", ge=0.0, le=1.0)
    check_duration_ms: int = Field(..., description="チェック実行時間(ms)", ge=0)


class SourcesHealthResponse(BaseModel):
    """ソースヘルスチェックレスポンス (6.4)"""
    summary: HealthCheckSummary = Field(..., description="ヘルスチェック概要")
    health_checks: List[SourceHealthItem] = Field(..., description="各ソースヘルスチェック結果")
    timestamp: datetime = Field(default_factory=datetime.now, description="チェック実行日時")
    next_check_at: datetime = Field(..., description="次回チェック予定日時")


# Webスクレイピング用スキーマ (6.2)
class ScrapeRequest(BaseModel):
    """Webスクレイピング実行リクエスト"""
    target_urls: List[str] = Field(..., description="スクレイピング対象URL一覧", min_items=1)
    date_range_start: Optional[datetime] = Field(None, description="取得開始日")
    date_range_end: Optional[datetime] = Field(None, description="取得終了日")
    source_type: DataSourceTypeEnum = Field(default=DataSourceTypeEnum.SCRAPING, description="ソース種別")
    options: Optional[Dict] = Field(None, description="スクレイピングオプション")


class ScrapeResultItem(BaseModel):
    """スクレイピング結果項目"""
    url: str = Field(..., description="スクレイピング対象URL")
    success: bool = Field(..., description="スクレイピング成功フラグ")
    records_extracted: int = Field(..., description="抽出レコード数", ge=0)
    data_preview: Optional[List[Dict]] = Field(None, description="データプレビュー（最大5件）")
    response_time_ms: int = Field(..., description="レスポンス時間(ms)", ge=0)
    error_message: Optional[str] = Field(None, description="エラーメッセージ")
    extracted_at: datetime = Field(default_factory=datetime.now, description="抽出日時")


class ScrapeResponse(BaseModel):
    """Webスクレイピング実行レスポンス (6.2)"""
    job_id: str = Field(..., description="スクレイピングジョブID")
    status: str = Field(..., description="実行状況")
    total_urls: int = Field(..., description="対象URL総数", ge=0)
    successful_urls: int = Field(..., description="成功URL数", ge=0)
    failed_urls: int = Field(..., description="失敗URL数", ge=0)
    total_records: int = Field(..., description="総抽出レコード数", ge=0)
    results: List[ScrapeResultItem] = Field(..., description="各URLスクレイピング結果")
    execution_time_ms: int = Field(..., description="総実行時間(ms)", ge=0)
    started_at: datetime = Field(default_factory=datetime.now, description="開始日時")
    completed_at: Optional[datetime] = Field(None, description="完了日時")


# CSV一括インポート用スキーマ (6.3)
class CSVImportRequest(BaseModel):
    """CSV一括インポート実行リクエスト"""
    file_path: str = Field(..., description="CSVファイルパス")
    source_type: DataSourceTypeEnum = Field(default=DataSourceTypeEnum.BOJ_CSV, description="データソース種別")
    date_column: str = Field(default="date", description="日付カラム名")
    rate_column: str = Field(default="close_rate", description="レートカラム名")
    skip_header: bool = Field(default=True, description="ヘッダー行スキップ")
    date_format: str = Field(default="%Y-%m-%d", description="日付フォーマット")
    validation_enabled: bool = Field(default=True, description="データ検証有効化")
    duplicate_handling: str = Field(default="skip", description="重複処理方式: skip, update, error")
    options: Optional[Dict] = Field(None, description="追加インポートオプション")


class CSVValidationResult(BaseModel):
    """CSV検証結果"""
    is_valid: bool = Field(..., description="検証結果")
    total_rows: int = Field(..., description="総行数", ge=0)
    valid_rows: int = Field(..., description="有効行数", ge=0)
    invalid_rows: int = Field(..., description="無効行数", ge=0)
    duplicate_rows: int = Field(..., description="重複行数", ge=0)
    missing_values: int = Field(..., description="欠損値数", ge=0)
    date_range_start: Optional[datetime] = Field(None, description="データ開始日")
    date_range_end: Optional[datetime] = Field(None, description="データ終了日")
    validation_errors: List[str] = Field(default_factory=list, description="検証エラー一覧")


class CSVImportResponse(BaseModel):
    """CSV一括インポート実行レスポンス (6.3)"""
    job_id: str = Field(..., description="インポートジョブID")
    status: str = Field(..., description="インポート状況")
    file_info: Dict[str, str] = Field(..., description="ファイル情報")
    validation: CSVValidationResult = Field(..., description="データ検証結果")
    import_summary: Dict[str, int] = Field(..., description="インポート概要統計")
    execution_time_ms: int = Field(..., description="実行時間(ms)", ge=0)
    started_at: datetime = Field(default_factory=datetime.now, description="開始日時")
    completed_at: Optional[datetime] = Field(None, description="完了日時")
    preview_data: Optional[List[Dict]] = Field(None, description="インポートデータプレビュー（最大10件）")


# エラーレスポンス用スキーマ
class SourcesErrorResponse(BaseModel):
    """データソースエラーレスポンス"""
    error: str = Field(..., description="エラータイプ")
    message: str = Field(..., description="エラーメッセージ")
    details: Optional[Dict] = Field(None, description="エラー詳細情報")
    timestamp: datetime = Field(default_factory=datetime.now, description="エラー発生日時")