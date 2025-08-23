# Forex Prediction System - デプロイメントガイド

## 📋 概要

このドキュメントは、Forex Prediction Systemの本番・ステージング・開発環境への統合デプロイメント手順を記載しています。

## 🏗️ アーキテクチャ

```
Frontend (React/Vite) → Backend (FastAPI) → Database (PostgreSQL) + Redis
```

## 📦 デプロイオプション

### 1. Docker Compose (推奨 - 開発/ステージング)

#### 環境別実行コマンド

```bash
# 開発環境
NODE_ENV=local docker-compose -f docker-compose.yml -f docker-compose.development.yml up -d

# ステージング環境
NODE_ENV=staging docker-compose -f docker-compose.yml -f docker-compose.staging.yml up -d

# 本番環境
NODE_ENV=production docker-compose -f docker-compose.yml -f docker-compose.production.yml up -d
```

#### 必要なファイル

- `docker-compose.yml` - ベース設定
- `docker-compose.development.yml` - 開発環境用オーバーライド
- `docker-compose.staging.yml` - ステージング環境用オーバーライド
- `docker-compose.production.yml` - 本番環境用オーバーライド
- `.env.local` / `.env.staging` / `.env.production` - 環境変数

### 2. Vercel (フロントエンド) + 外部Backend

#### フロントエンドデプロイ

```bash
cd frontend
vercel --prod
```

#### 環境変数設定 (Vercel Dashboard)

```
VITE_API_URL=https://your-backend-api.com
VITE_WS_URL=wss://your-backend-api.com
NODE_ENV=production
```

### 3. Railway

#### プロジェクト設定

```bash
# Railway CLIでデプロイ
railway login
railway init
railway up
```

#### 環境変数設定

Railway Dashboardで以下を設定：

```
DATABASE_URL=postgresql://...
REDIS_URL=redis://...
SECRET_KEY=your-secret-key
DEBUG=False
```

### 4. Render

#### render.yamlを使用した自動デプロイ

1. GitHubリポジトリをRenderに接続
2. `render.yaml`が自動検出され、サービスが作成される
3. 環境変数は自動設定される

## 🔧 環境変数設定

### 必須環境変数

| 変数名 | 開発環境 | ステージング | 本番環境 | 説明 |
|--------|----------|-------------|----------|------|
| `NODE_ENV` | local | staging | production | 環境識別子 |
| `DATABASE_URL` | localhost:5432 | staging-db.com | production-db.com | DB接続URL |
| `SECRET_KEY` | dev-key | staging-key | production-key | API秘密鍵 |
| `DEBUG` | True | False | False | デバッグモード |
| `LOG_LEVEL` | DEBUG | WARNING | ERROR | ログレベル |

### フロントエンド環境変数

| 変数名 | 開発環境 | ステージング | 本番環境 |
|--------|----------|-------------|----------|
| `VITE_API_URL` | http://localhost:8173 | https://api-staging.com | https://api.com |
| `VITE_WS_URL` | ws://localhost:8173 | wss://api-staging.com | wss://api.com |

## 🚀 デプロイ手順

### 初回デプロイ

1. **環境変数ファイルの準備**
   ```bash
   cp .env.local.example .env.local
   # 必要な値を設定
   ```

2. **データベースの初期化**
   ```bash
   # Docker環境の場合
   docker-compose up postgres -d
   
   # Backend container内で実行
   docker-compose exec backend alembic upgrade head
   ```

3. **アプリケーションの起動**
   ```bash
   # 全サービス起動
   NODE_ENV=local docker-compose up -d
   
   # ヘルスチェック
   curl http://localhost:8173/docs
   curl http://localhost:3173
   ```

### 本番デプロイ

1. **事前チェック**
   ```bash
   # テストの実行
   cd backend && python -m pytest tests/
   
   # ビルドテスト
   cd frontend && npm run build
   ```

2. **データベースマイグレーション**
   ```bash
   # Alembicマイグレーション
   alembic upgrade head
   ```

3. **ゼロダウンタイムデプロイ**
   ```bash
   # Blue-Greenデプロイ（Docker Swarm使用時）
   docker stack deploy -c docker-compose.yml -c docker-compose.production.yml forex-system
   ```

## 🔍 ヘルスチェック・モニタリング

### エンドポイント

- **Backend**: `GET /docs` - API仕様確認
- **Frontend**: `GET /health` - フロントエンド生存確認
- **Database**: PostgreSQL接続テスト

### ログ確認

```bash
# Docker環境
docker-compose logs -f backend
docker-compose logs -f frontend

# Railway
railway logs

# Render
render logs service-name
```

## 🛠️ トラブルシューティング

### よくある問題

1. **CORS エラー**
   ```
   解決策: .env.*ファイルのCORS_ORIGINSを確認
   ```

2. **データベース接続エラー**
   ```
   解決策: DATABASE_URLとPostgreSQLの起動状態を確認
   ```

3. **ビルドエラー**
   ```
   解決策: Node.jsバージョンとnpm依存関係を確認
   ```

### デバッグコマンド

```bash
# サービス状態確認
docker-compose ps

# ネットワーク確認
docker network ls
docker network inspect forex_network

# コンテナ内部確認
docker-compose exec backend bash
docker-compose exec frontend sh
```

## 🔐 セキュリティチェックリスト

- [ ] SECRET_KEYが本番用の強力なキーに設定されている
- [ ] DEBUGがFalseに設定されている（本番環境）
- [ ] CORS_ORIGINSが適切なドメインに限定されている
- [ ] データベース認証情報が安全に管理されている
- [ ] HTTPS/TLSが有効化されている
- [ ] セキュリティヘッダーが設定されている

## 📊 パフォーマンス最適化

### 推奨設定

1. **Backend**
   - Gunicorn workers: CPU数 × 2 + 1
   - Memory limit: 1GB (staging), 2GB (production)

2. **Frontend**
   - CDN配信: Vercel/Cloudflare
   - 画像最適化: WebP対応
   - Bundle分割: Code splitting

3. **Database**
   - Connection pooling: SQLAlchemy pool設定
   - インデックス最適化: よく使用するクエリ

## 🔄 CI/CD パイプライン

### GitHub Actions設定例

```yaml
name: Deploy
on:
  push:
    branches: [main]

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Deploy to staging
        run: |
          # デプロイスクリプト実行
```

## 📞 サポート・問い合わせ

デプロイに関する問題や質問については、プロジェクトのIssueトラッカーまでお寄せください。

---

**最終更新**: 2024年8月
**バージョン**: 1.0.0