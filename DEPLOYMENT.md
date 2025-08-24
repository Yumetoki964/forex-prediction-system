# 本番環境デプロイメントガイド

## 📋 目次
1. [前提条件](#前提条件)
2. [クイックデプロイ](#クイックデプロイ)
3. [詳細セットアップ](#詳細セットアップ)
4. [設定カスタマイズ](#設定カスタマイズ)
5. [トラブルシューティング](#トラブルシューティング)
6. [メンテナンス](#メンテナンス)

## 前提条件

### システム要件
- **OS**: Ubuntu 20.04+ / CentOS 8+ / macOS 11+
- **CPU**: 4コア以上推奨
- **RAM**: 8GB以上（16GB推奨）
- **Storage**: 50GB以上の空き容量
- **Network**: インターネット接続必須

### 必須ソフトウェア
```bash
# Dockerのインストール
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh

# Docker Composeのインストール
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose

# 確認
docker --version
docker-compose --version
```

## クイックデプロイ

### 1分でデプロイ完了
```bash
# プロジェクトのクローン
git clone https://github.com/your-org/forex-prediction-system.git
cd forex-prediction-system

# デプロイ実行
./deploy.sh
```

## 詳細セットアップ

### 1. 環境変数の設定

```bash
# 本番用環境変数ファイルの作成
cp backend/.env.example backend/.env.production

# 編集
vim backend/.env.production
```

重要な設定項目:
```env
# データベース（必須）
DATABASE_URL=postgresql://forex_user:your_secure_password@db:5432/forex_prediction_db

# セキュリティ（必須・変更必須）
SECRET_KEY=your-very-long-random-secret-key-here
JWT_SECRET_KEY=another-very-long-random-secret-key

# 外部API（オプション）
YAHOO_FINANCE_API_KEY=your-api-key
ALPHA_VANTAGE_API_KEY=your-api-key

# 本番環境設定
ENVIRONMENT=production
DEBUG=false
```

### 2. SSL証明書の設定（HTTPS）

```bash
# Let's Encrypt証明書の取得
sudo apt-get update
sudo apt-get install certbot
sudo certbot certonly --standalone -d your-domain.com

# 証明書をnginxディレクトリにコピー
cp /etc/letsencrypt/live/your-domain.com/fullchain.pem ./nginx/certs/
cp /etc/letsencrypt/live/your-domain.com/privkey.pem ./nginx/certs/
```

### 3. データベースの初期化

```bash
# コンテナ起動
docker-compose up -d db

# データベース初期化
docker-compose exec db psql -U forex_user -d forex_prediction_db -f /docker-entrypoint-initdb.d/init.sql

# マイグレーション実行
docker-compose run --rm backend alembic upgrade head
```

### 4. 全サービスの起動

```bash
# ビルドと起動
docker-compose build
docker-compose up -d

# 状態確認
docker-compose ps

# ログ確認
docker-compose logs -f
```

## 設定カスタマイズ

### ポート変更
`docker-compose.yml`を編集:
```yaml
services:
  frontend:
    ports:
      - "8080:80"  # 80から8080に変更
  backend:
    ports:
      - "8001:8000"  # 8000から8001に変更
```

### メモリ制限の設定
```yaml
services:
  backend:
    deploy:
      resources:
        limits:
          cpus: '2'
          memory: 4G
        reservations:
          cpus: '1'
          memory: 2G
```

### ログローテーション
```yaml
services:
  backend:
    logging:
      driver: "json-file"
      options:
        max-size: "10m"
        max-file: "3"
```

## トラブルシューティング

### よくある問題と解決方法

#### 1. ポート競合エラー
```bash
# 使用中のポート確認
sudo lsof -i :8000
sudo lsof -i :80

# 別のポートに変更するか、既存サービスを停止
sudo systemctl stop nginx  # 例
```

#### 2. データベース接続エラー
```bash
# データベースコンテナの確認
docker-compose logs db

# 接続テスト
docker-compose exec db pg_isready -U forex_user

# 手動接続
docker-compose exec db psql -U forex_user -d forex_prediction_db
```

#### 3. ビルドエラー
```bash
# キャッシュクリアして再ビルド
docker-compose build --no-cache

# イメージの削除と再構築
docker-compose down
docker system prune -a
docker-compose build
```

#### 4. メモリ不足
```bash
# Dockerのメモリ制限確認
docker info | grep Memory

# スワップメモリの追加（Linux）
sudo fallocate -l 4G /swapfile
sudo chmod 600 /swapfile
sudo mkswap /swapfile
sudo swapon /swapfile
```

## メンテナンス

### 定期バックアップ

```bash
# データベースバックアップ
docker-compose exec db pg_dump -U forex_user forex_prediction_db > backup_$(date +%Y%m%d).sql

# 全データバックアップ
docker run --rm -v forex-prediction-system_postgres_data:/data -v $(pwd):/backup alpine tar czf /backup/postgres_backup_$(date +%Y%m%d).tar.gz -C /data .
```

### アップデート手順

```bash
# 1. 最新コードの取得
git pull origin main

# 2. バックアップ実行
./scripts/backup.sh

# 3. サービス停止
docker-compose down

# 4. 再ビルドと起動
docker-compose build
docker-compose up -d

# 5. マイグレーション実行
docker-compose exec backend alembic upgrade head

# 6. 動作確認
./test_production.sh
```

### ログ管理

```bash
# ログの確認
docker-compose logs -f backend  # バックエンドログ
docker-compose logs -f frontend # フロントエンドログ
docker-compose logs -f db       # データベースログ

# ログのエクスポート
docker-compose logs > system_logs_$(date +%Y%m%d).log

# ログのクリーンアップ
docker-compose logs --tail=1000 > recent_logs.log
```

### パフォーマンス監視

```bash
# リソース使用状況
docker stats

# 詳細な状態確認
docker-compose exec backend python -m app.utils.health_check

# Prometheusダッシュボード（有効な場合）
http://localhost:9090

# Grafanaダッシュボード（有効な場合）
http://localhost:3000
```

## セキュリティ対策

### 1. ファイアウォール設定
```bash
# UFW（Ubuntu）
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
sudo ufw allow 22/tcp
sudo ufw enable

# firewalld（CentOS）
sudo firewall-cmd --permanent --add-service=http
sudo firewall-cmd --permanent --add-service=https
sudo firewall-cmd --reload
```

### 2. 定期的なセキュリティアップデート
```bash
# システムアップデート
sudo apt-get update && sudo apt-get upgrade

# Dockerイメージの更新
docker-compose pull
docker-compose build --pull
```

### 3. アクセス制限
nginx設定で特定IPのみ許可:
```nginx
location /api/admin {
    allow 192.168.1.0/24;
    deny all;
    proxy_pass http://backend:8000;
}
```

## サポート

問題が解決しない場合:
1. [GitHub Issues](https://github.com/your-org/forex-prediction-system/issues)で報告
2. ログファイルを添付（個人情報は削除）
3. 実行環境の詳細を記載

## 次のステップ

デプロイ完了後:
1. 管理者パスワードの変更
2. APIキーの設定
3. バックアップスケジュールの設定
4. 監視アラートの設定
5. 本番データの投入

---

**重要**: 本番環境では必ずセキュリティ設定を確認し、デフォルトパスワードを変更してください。