# Forex Prediction System (為替予測システム)

## 📊 概要

AI技術を活用した高精度な為替レート予測システムです。リアルタイムデータ収集、機械学習による予測、バックテスト機能を統合した総合的な為替取引支援プラットフォームです。

## 🚀 主要機能

### 1. **リアルタイム為替予測**
- USD/JPYペアの高精度予測
- 1週間・1ヶ月先の予測
- 信頼度スコア付き予測結果

### 2. **テクニカル分析**
- 20種類以上のテクニカル指標
- カスタマイズ可能なチャート表示
- サポート・レジスタンスレベル自動検出

### 3. **バックテスト機能**
- 複数の取引戦略テスト
- パフォーマンス指標の詳細分析
- リスク管理パラメータ最適化

### 4. **アラート&通知**
- 価格変動アラート
- 予測シグナル通知
- カスタマイズ可能な通知条件

## 🛠️ 技術スタック

### Backend
- **Framework**: FastAPI (Python 3.11)
- **Database**: PostgreSQL 15
- **Cache**: Redis 7
- **ML Libraries**: scikit-learn, TensorFlow
- **API Documentation**: OpenAPI/Swagger

### Frontend
- **Framework**: React 18 + TypeScript
- **UI Library**: Material-UI v5
- **Charts**: ApexCharts
- **State Management**: React Query
- **Build Tool**: Vite

### Infrastructure
- **Container**: Docker & Docker Compose
- **CI/CD**: GitHub Actions
- **Monitoring**: Prometheus + Grafana
- **Reverse Proxy**: Nginx

## 📦 インストール

### 前提条件
- Docker & Docker Compose
- Git
- 8GB以上のRAM推奨

### クイックスタート

```bash
# 1. リポジトリのクローン
git clone https://github.com/your-org/forex-prediction-system.git
cd forex-prediction-system

# 2. 環境変数の設定
cp backend/.env.example backend/.env.production
# .env.productionを編集して必要な値を設定

# 3. デプロイスクリプトの実行
chmod +x deploy.sh
./deploy.sh
```

### 手動デプロイ

```bash
# Docker Composeで起動
docker-compose up -d

# ログの確認
docker-compose logs -f

# サービスの停止
docker-compose down
```

## 🔧 設定

### 環境変数

`backend/.env.production`:
```env
DATABASE_URL=postgresql://forex_user:forex_pass@db:5432/forex_prediction_db
SECRET_KEY=your-secret-key-here
JWT_SECRET_KEY=your-jwt-secret-here
YAHOO_FINANCE_API_KEY=your-api-key
```

### データベース初期化

```bash
# マイグレーション実行
docker-compose exec backend alembic upgrade head

# 初期データ投入
docker-compose exec db psql -U forex_user -d forex_prediction_db -f /docker-entrypoint-initdb.d/init.sql
```

## 📊 使用方法

### 1. システムへのアクセス

デプロイ後、以下のURLでアクセス可能:
- **Frontend**: http://localhost
- **Backend API**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs
- **pgAdmin**: http://localhost:5050 (開発環境のみ)

### 2. ログイン

デフォルト管理者アカウント:
- Username: `admin`
- Password: `password` (初回ログイン後に変更してください)

### 3. 主要ページ

- **ダッシュボード**: リアルタイムレートと予測サマリー
- **詳細予測分析**: チャートとテクニカル指標の詳細表示
- **バックテスト**: 戦略のバックテスト実行と結果分析
- **データ管理**: データソースとインポート設定
- **設定**: システム設定とカスタマイズ

## 🧪 テスト

### バックエンドテスト
```bash
cd backend
pytest tests/
```

### フロントエンドテスト
```bash
cd frontend
npm test
```

### E2Eテスト
```bash
cd frontend
npm run test:e2e
```

## 🚀 本番環境デプロイ

### AWS/GCPへのデプロイ

1. クラウドインスタンスの準備
2. Dockerとdocker-composeのインストール
3. リポジトリのクローンとデプロイスクリプトの実行

### Kubernetes (K8s)デプロイ

```bash
# Helmチャートを使用
helm install forex-prediction ./k8s/helm-chart
```

## 📈 モニタリング

### Prometheus メトリクス
- http://localhost:9090
- カスタムメトリクスの追加可能

### Grafana ダッシュボード
- http://localhost:3000
- デフォルトログイン: admin/admin_password

## 🔒 セキュリティ

- JWT認証によるAPIセキュリティ
- HTTPS通信（本番環境）
- SQLインジェクション対策
- XSS/CSRF保護
- レート制限実装

## 📝 API仕様

詳細なAPI仕様は以下で確認可能:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

主要エンドポイント:
- `GET /api/rates/current` - 現在のレート取得
- `GET /api/predictions/latest` - 最新予測取得
- `POST /api/backtest/run` - バックテスト実行
- `GET /api/signals/current` - 取引シグナル取得

## 🤝 貢献

プルリクエストを歓迎します。大きな変更の場合は、まずissueを開いて変更内容を議論してください。

## 📄 ライセンス

[MIT License](LICENSE)

## 📞 サポート

- Issue: [GitHub Issues](https://github.com/your-org/forex-prediction-system/issues)
- Email: support@forex-prediction.com
- Documentation: [Wiki](https://github.com/your-org/forex-prediction-system/wiki)

## 🎯 ロードマップ

- [ ] 複数通貨ペアサポート
- [ ] AIモデルの精度向上
- [ ] モバイルアプリ開発
- [ ] リアルタイム取引API統合
- [ ] 多言語対応

---

**Note**: このシステムは教育・研究目的で開発されています。実際の取引に使用する際は、リスクを十分に理解した上でご利用ください。