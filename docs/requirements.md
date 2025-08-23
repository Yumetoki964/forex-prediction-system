# Forex Prediction System - 要件定義書

## 1. プロジェクト概要

### 1.1 成果目標
1990年からのドル円為替データを基に、投資判断に活用できる1週間〜1ヶ月後の為替レート予測と、リスク評価を含む包括的な予測システムを構築する

### 1.2 成功指標

#### 定量的指標
- 予測精度：1週間後の予測で±1.5%以内を70%以上、1ヶ月後で±3%以内を60%以上達成
- データ収集率：1990年以降の営業日データを98%以上取得
- 予測更新頻度：毎日自動で1週間・2週間・3週間・1ヶ月後の予測を生成
- リスク指標：ボラティリティと信頼区間を全予測に付与
- バックテスト精度：過去5年分の検証で60%以上の的中率

#### 定性的指標
- 投資判断の支援：買い/売り/待機のシグナル表示が明確
- リスクの可視化：予測の信頼度と変動リスクが一目で分かる
- 根拠の透明性：テクニカル指標・経済指標の影響度を表示
- アラート機能：重要な変動予測時に通知
- 過去検証：バックテスト結果で予測モデルの信頼性を確認可能

## 2. 技術スタック（固定）

### 2.1 フロントエンド
- **フレームワーク**: React 18
- **ビルドツール**: Vite 5
- **言語**: TypeScript 5
- **UIライブラリ**: MUI v5 (Material-UI)
- **状態管理**: Zustand / TanStack Query
- **ルーティング**: React Router v6
- **APIクライアント**: Axios / OpenAPI Generator

### 2.2 バックエンド
- **言語**: Python 3.11+
- **フレームワーク**: FastAPI 0.100+
- **ORM**: SQLAlchemy 2.0 + Alembic
- **バリデーション**: Pydantic v2
- **認証**: FastAPI-Users / Auth0
- **非同期タスク**: Celery + Redis
- **API文書**: OpenAPI 3.0（自動生成）

### 2.3 データベース
- **メインDB**: PostgreSQL 15+ (Railway PostgreSQL推奨)
- **環境統一**: 開発・ステージング・本番すべてRailway PostgreSQL
- **キャッシュ**: Redis
- **マイグレーション**: SQLAlchemy + Alembic
- **ベクターDB**: Qdrant（RAG用、必要に応じて）

### 2.4 インフラ＆デプロイ
- **フロントエンド**: Vercel (React/Vite最適化)
- **バックエンド**: GCP Cloud Run (FastAPI最適化)
- **データベース**: NEON
- **AI処理**: RunPod (GPU処理) + OpenAI API
- **ベクターDB**: Qdrant Cloud (東京リージョン)
- **CI/CD**: GitHub Actions統合

### 2.5 開発環境＆ツール
- **Python**: 3.11+
- **Node.js**: 20.x LTS
- **パッケージマネージャー**: Poetry（Python）, pnpm（JavaScript）
- **コード品質**: Black, Ruff, ESLint, Prettier

## 3. ページ詳細仕様

### 3.1 P-001: 予測ダッシュボード

#### 目的
現在レートと最大1ヶ月先の予測を統合表示し、投資判断に必要な情報を一画面で提供

#### 主要機能
- 現在レート表示（5分毎更新）
- 1週間〜1ヶ月予測（1週間、2週間、3週間、1ヶ月）
- 5段階売買シグナル（強い売り/売り/待機/買い/強い買い）
- リスク指標（ボラティリティ、信頼区間）
- アクティブアラート表示

#### エンドポイント（FastAPI形式）
```python
@router.get("/api/rates/current")
async def get_current_rate() -> CurrentRateResponse:
    """現在のドル円レートを取得"""

@router.get("/api/predictions/latest")
async def get_latest_predictions() -> PredictionResponse:
    """最新の1週間〜1ヶ月予測を取得"""

@router.get("/api/signals/current")
async def get_current_signal() -> SignalResponse:
    """現在の売買シグナル（5段階）を取得"""

@router.get("/api/metrics/risk")
async def get_risk_metrics() -> RiskMetricsResponse:
    """リスク指標（ボラティリティ・信頼区間）を取得"""

@router.get("/api/alerts/active")
async def get_active_alerts() -> AlertResponse:
    """アクティブなアラートを取得"""
```

#### 処理フロー
1. 現在レートと最新予測データを並行取得
2. リスク指標とシグナルを計算
3. アクティブアラートを確認・表示
4. 5分毎自動更新

#### データモデル（Pydantic）
```python
class CurrentRateResponse(BaseModel):
    rate: float
    timestamp: datetime
    change_24h: float
    change_percentage_24h: float

class PredictionResponse(BaseModel):
    predictions: List[PredictionItem]
    confidence_level: float
    generated_at: datetime

class PredictionItem(BaseModel):
    period: str  # "1week", "2weeks", "3weeks", "1month"
    predicted_rate: float
    confidence_interval: Tuple[float, float]
    volatility: float
```

### 3.2 P-002: 詳細予測分析

#### 目的
予測の根拠となるテクニカル指標と経済指標の影響度を可視化し、予測精度向上の洞察を提供

#### 主要機能
- チャート表示（3ヶ月〜3年間、期間選択可能）
- テクニカル指標（MA、RSI、MACD、ボリンジャーバンド）
- 経済指標影響度分析
- 予測モデルの内部ロジック表示

#### エンドポイント（FastAPI形式）
```python
@router.get("/api/charts/historical")
async def get_historical_chart(period: str, indicators: List[str]) -> ChartResponse:
    """指定期間の為替チャートとテクニカル指標を取得"""

@router.get("/api/predictions/detailed")
async def get_detailed_predictions() -> DetailedPredictionResponse:
    """詳細な予測分析データを取得"""

@router.get("/api/indicators/technical")
async def get_technical_indicators() -> TechnicalIndicatorsResponse:
    """テクニカル指標の現在値と推移を取得"""

@router.get("/api/indicators/economic")
async def get_economic_impact() -> EconomicImpactResponse:
    """経済指標の影響度分析を取得"""
```

### 3.3 P-003: バックテスト検証

#### 目的
過去データを使用した予測精度検証とリターン分析で、システムの信頼性を定量的に評価

#### 主要機能
- 過去5年分のバックテスト結果（デフォルト設定）
- 初期資金100万円でのシミュレーション
- 収益曲線とドローダウン分析
- シャープレシオと勝率表示
- カスタムバックテスト実行

#### エンドポイント（FastAPI形式）
```python
@router.post("/api/backtest/run")
async def run_backtest(config: BacktestConfig) -> BacktestJobResponse:
    """バックテストを実行（非同期）"""

@router.get("/api/backtest/results/{job_id}")
async def get_backtest_results(job_id: str) -> BacktestResultsResponse:
    """バックテスト結果を取得"""

@router.get("/api/backtest/metrics/{job_id}")
async def get_backtest_metrics(job_id: str) -> BacktestMetricsResponse:
    """バックテスト評価指標を取得"""

@router.get("/api/backtest/trades/{job_id}")
async def get_backtest_trades(job_id: str) -> BacktestTradesResponse:
    """バックテストの取引履歴を取得"""
```

### 3.4 P-004: データ管理

#### 目的
1990年からの為替データの自動収集・品質監視・修復を担当し、システムの基盤データを確保

#### 主要機能
- 毎日朝6時自動データ収集
- 線形補間による欠損値修復
- データソース自動切り替え
- データ品質監視とアラート

#### エンドポイント（FastAPI形式）
```python
@router.get("/api/data/status")
async def get_data_status() -> DataStatusResponse:
    """データ収集状況とカバレッジを取得"""

@router.post("/api/data/collect")
async def trigger_data_collection() -> CollectionJobResponse:
    """データ収集を手動実行"""

@router.get("/api/data/quality")
async def get_data_quality() -> DataQualityResponse:
    """データ品質レポートを取得"""

@router.post("/api/data/repair")
async def repair_missing_data(period: DateRange) -> RepairJobResponse:
    """指定期間の欠損データを修復"""

@router.get("/api/data/sources")
async def get_data_sources() -> DataSourcesResponse:
    """データソースの稼働状況を取得"""
```

### 3.5 P-005: 予測設定

#### 目的
予測モデルのパラメーター調整とアラート設定により、ユーザー固有のニーズに対応

#### 主要機能
- アンサンブルモデル設定（LSTM+XGBoost比重調整）
- 予測感度調整（保守的/標準/積極的）
- アラート設定（メール・ブラウザ通知）
- 予測テスト実行

#### エンドポイント（FastAPI形式）
```python
@router.get("/api/settings/prediction")
async def get_prediction_settings() -> PredictionSettingsResponse:
    """現在の予測設定を取得"""

@router.put("/api/settings/prediction")
async def update_prediction_settings(settings: PredictionSettings) -> UpdateResponse:
    """予測設定を更新"""

@router.get("/api/settings/alerts")
async def get_alert_settings() -> AlertSettingsResponse:
    """アラート設定を取得"""

@router.put("/api/settings/alerts")
async def update_alert_settings(settings: AlertSettings) -> UpdateResponse:
    """アラート設定を更新"""

@router.post("/api/settings/test")
async def test_prediction_settings() -> TestResultResponse:
    """現在設定での予測テストを実行"""
```

### 3.6 P-006: データソース管理

#### 目的
複数データソースの統合管理とフォールバック機能で、安定したデータ供給を保証

#### 主要機能
- CSV一括取得（日銀データ）
- Webスクレイピング（Yahoo Finance）
- APIバックアップ（Alpha Vantage無料API）
- ソース健全性監視

#### エンドポイント（FastAPI形式）
```python
@router.get("/api/sources/status")
async def get_sources_status() -> SourcesStatusResponse:
    """全データソースの稼働状況を取得"""

@router.post("/api/sources/scrape")
async def trigger_scraping() -> ScrapingJobResponse:
    """Webスクレイピングを手動実行"""

@router.post("/api/sources/csv-import")
async def import_csv_data(file: UploadFile) -> ImportJobResponse:
    """CSVファイルから履歴データを一括インポート"""

@router.get("/api/sources/health")
async def check_sources_health() -> SourcesHealthResponse:
    """データソースのヘルスチェックを実行"""
```

## 4. データベース設計概要

### 主要テーブル（SQLAlchemy）
```python
class ExchangeRate(Base):
    __tablename__ = "exchange_rates"
    
    id = Column(Integer, primary_key=True, index=True)
    date = Column(Date, unique=True, index=True)
    rate = Column(Float, nullable=False)
    open_rate = Column(Float)
    close_rate = Column(Float)
    high_rate = Column(Float)
    low_rate = Column(Float)
    volume = Column(BigInteger)
    source = Column(String(50))
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, onupdate=datetime.utcnow)

class Prediction(Base):
    __tablename__ = "predictions"
    
    id = Column(Integer, primary_key=True, index=True)
    prediction_date = Column(Date, index=True)
    target_date = Column(Date, index=True)
    predicted_rate = Column(Float, nullable=False)
    confidence_interval_lower = Column(Float)
    confidence_interval_upper = Column(Float)
    volatility = Column(Float)
    model_version = Column(String(50))
    created_at = Column(DateTime, default=datetime.utcnow)

class TradingSignal(Base):
    __tablename__ = "trading_signals"
    
    id = Column(Integer, primary_key=True, index=True)
    date = Column(Date, index=True)
    signal_type = Column(String(20))  # strong_sell, sell, hold, buy, strong_buy
    confidence = Column(Float)
    reasoning = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
```

## 5. 制約事項

### 外部API制限
- **Alpha Vantage無料API**: 1日500リクエスト、1分5リクエスト制限
- **Yahoo Finance**: レート制限なし（スクレイピング）
- **日銀CSV**: 手動ダウンロード対応

### 技術的制約
- **予測期間**: 最大1ヶ月先まで（それ以降は精度が大幅低下）
- **データ更新頻度**: 営業日のみ（土日祝は更新なし）
- **バックテスト実行時間**: 5年分で約10-15分

## 6. 主要VSA処理連鎖

### VSA-001: 日次予測更新処理
**処理フロー**:
1. `POST /api/data/collect` - 最新レートデータ収集
2. **内部処理連鎖**:
   - テクニカル指標計算
   - LSTMモデル予測実行
   - XGBoostモデル予測実行
   - アンサンブル予測生成
3. `POST /api/predictions/generate` - 予測結果保存
4. `POST /api/signals/calculate` - 売買シグナル生成

**外部依存**: Yahoo Finance、日銀データ、Alpha Vantage API

### VSA-002: バックテスト実行処理
**処理フロー**:
1. `POST /api/backtest/run` - バックテスト設定受信
2. **内部処理連鎖**:
   - 履歴データ取得・検証
   - モデル予測実行（時系列順）
   - 取引シミュレーション
   - パフォーマンス指標計算
3. `GET /api/backtest/results/{job_id}` - 結果取得

**外部依存**: なし（内部データのみ）

## 7. Docker環境構成

### docker-compose.yml 基本構成
```yaml
services:
  backend:    # FastAPI + Python 3.11
    - 予測モデル（LSTM + XGBoost）
    - データ収集・処理エンジン
    - API エンドポイント
  frontend:   # React + Vite + TypeScript
    - ダッシュボード UI
    - チャート可視化
    - 設定管理画面
  db:         # PostgreSQL 15
    - 為替レートデータ
    - 予測結果
    - 設定情報
  redis:      # キャッシュ・セッション管理
    - API レスポンスキャッシュ
    - 予測結果一時保存
```

## 8. 必要な外部サービス・アカウント

### 必須サービス
| サービス名 | 用途 | 取得先 | 備考 |
|-----------|------|--------|------|
| なし | データ取得は全て無料ソース | - | APIキー不要設計 |

### オプションサービス
| サービス名 | 用途 | 取得先 | 備考 |
|-----------|------|--------|------|
| Alpha Vantage | バックアップAPI | alphavantage.co | 無料プラン（1日500リクエスト） |
| SendGrid | アラートメール送信 | sendgrid.com | 月100通まで無料 |

## 9. 今後の拡張予定

### フェーズ2
- 他通貨ペア対応（ユーロ/ドル、ポンド/ドル）
- 高度なテクニカル指標追加
- ポートフォリオ管理機能

### フェーズ3
- 機械学習モデルの改良（Transformer導入）
- リアルタイム予測（分単位更新）
- ソーシャルセンチメント分析統合

---