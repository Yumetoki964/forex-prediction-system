# インターネット公開ガイド

## 🚀 推奨デプロイメント方法

### 方法1: クラウドサービス利用（推奨）

#### A. **Vercel + Railway** (最も簡単・無料枠あり)

**メリット**: 
- 設定が簡単
- 無料枠で始められる
- 自動HTTPS
- 自動デプロイ

**手順**:

1. **Frontend (Vercel)**
```bash
# Vercel CLIインストール
npm i -g vercel

# フロントエンドディレクトリで実行
cd frontend
vercel

# 質問に答えていく
# - Setup and deploy? → Yes
# - Which scope? → 自分のアカウント選択
# - Link to existing project? → No
# - Project name? → forex-prediction-frontend
# - Directory? → ./
# - Build command? → npm run build
# - Output directory? → dist
```

2. **Backend (Railway)**
```bash
# Railway CLIインストール
npm i -g @railway/cli

# バックエンドディレクトリで実行
cd backend
railway login
railway init
railway up

# 環境変数設定（Railway Dashboard上で）
# DATABASE_URL, SECRET_KEY等を設定
```

3. **Database (Railway PostgreSQL)**
```bash
# Railway上でPostgreSQLサービス追加
railway add postgresql

# 接続情報をバックエンドの環境変数に設定
```

#### B. **AWS (本格運用向け)**

**必要なサービス**:
- EC2 (アプリケーション)
- RDS (PostgreSQL)
- S3 (静的ファイル)
- CloudFront (CDN)
- Route 53 (DNS)

**セットアップ手順**:

1. **EC2インスタンス作成**
```bash
# AWS CLIでインスタンス作成
aws ec2 run-instances \
  --image-id ami-0c55b159cbfafe1f0 \
  --instance-type t3.medium \
  --key-name your-key-pair \
  --security-groups your-security-group
```

2. **インスタンスにSSH接続**
```bash
ssh -i your-key.pem ec2-user@your-instance-ip
```

3. **Dockerインストール & デプロイ**
```bash
# Docker インストール
sudo yum update -y
sudo yum install docker -y
sudo service docker start
sudo usermod -a -G docker ec2-user

# Docker Compose インストール
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose

# プロジェクトクローン
git clone https://github.com/your-repo/forex-prediction-system.git
cd forex-prediction-system

# 環境変数設定
cp backend/.env.example backend/.env.production
nano backend/.env.production

# デプロイ
./deploy.sh
```

#### C. **Google Cloud Platform**

**必要なサービス**:
- Compute Engine (VM)
- Cloud SQL (PostgreSQL)
- Cloud Storage (静的ファイル)

**デプロイ手順**:

```bash
# GCP CLIセットアップ
gcloud init

# プロジェクト作成
gcloud projects create forex-prediction-system

# Compute Engineインスタンス作成
gcloud compute instances create forex-app \
  --zone=asia-northeast1-a \
  --machine-type=e2-medium \
  --image-family=ubuntu-2004-lts \
  --image-project=ubuntu-os-cloud

# SSHアクセス
gcloud compute ssh forex-app

# 以降はAWSと同様の手順
```

### 方法2: VPS利用（コスト重視）

#### 推奨VPSサービス
- **Vultr**: $6/月〜
- **DigitalOcean**: $6/月〜
- **Linode**: $5/月〜
- **さくらVPS**: ¥643/月〜

**セットアップ手順**:

1. **VPS契約・初期設定**
```bash
# VPSにSSH接続
ssh root@your-vps-ip

# ユーザー作成
adduser forex-admin
usermod -aG sudo forex-admin

# SSH設定
nano /etc/ssh/sshd_config
# PermitRootLogin no
# PasswordAuthentication no
systemctl restart sshd
```

2. **ファイアウォール設定**
```bash
# UFW設定
ufw allow 22/tcp
ufw allow 80/tcp
ufw allow 443/tcp
ufw enable
```

3. **Docker環境構築**
```bash
# Dockerインストール
curl -fsSL https://get.docker.com -o get-docker.sh
sh get-docker.sh

# Docker Composeインストール
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose
```

4. **プロジェクトデプロイ**
```bash
# プロジェクトクローン
git clone https://github.com/your-repo/forex-prediction-system.git
cd forex-prediction-system

# 本番環境設定
cp backend/.env.example backend/.env.production
nano backend/.env.production

# デプロイ実行
./deploy.sh
```

## 🔒 SSL証明書設定（必須）

### Let's Encrypt (無料SSL)

```bash
# Certbotインストール
sudo apt-get update
sudo apt-get install certbot python3-certbot-nginx

# 証明書取得
sudo certbot --nginx -d your-domain.com -d www.your-domain.com

# 自動更新設定
sudo crontab -e
# 追加: 0 0 * * * /usr/bin/certbot renew --quiet
```

## 🌐 ドメイン設定

### 1. ドメイン取得
- **Namecheap**: $8.88/年〜
- **Google Domains**: $12/年〜
- **お名前.com**: ¥1,408/年〜

### 2. DNS設定
```
A Record: @ → サーバーIPアドレス
A Record: www → サーバーIPアドレス
```

### 3. Nginx設定更新
```nginx
server {
    listen 80;
    server_name your-domain.com www.your-domain.com;
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name your-domain.com www.your-domain.com;
    
    ssl_certificate /etc/letsencrypt/live/your-domain.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/your-domain.com/privkey.pem;
    
    # ... 既存の設定 ...
}
```

## 📊 本番環境チェックリスト

### デプロイ前確認事項

- [ ] **環境変数設定**
  - [ ] SECRET_KEY変更済み
  - [ ] JWT_SECRET_KEY変更済み
  - [ ] DEBUG=false設定
  - [ ] 本番データベースURL設定

- [ ] **セキュリティ**
  - [ ] HTTPSの有効化
  - [ ] ファイアウォール設定
  - [ ] 管理者パスワード変更
  - [ ] SSH鍵認証の設定

- [ ] **バックアップ**
  - [ ] データベースバックアップ設定
  - [ ] 自動バックアップのcron設定

- [ ] **監視**
  - [ ] UptimeRobotなどの死活監視
  - [ ] エラーログ監視設定

## 💰 コスト見積もり

### 最小構成（個人利用）
- VPS: $5-10/月
- ドメイン: $10-15/年
- **合計: 約$6-12/月**

### 推奨構成（小規模ビジネス）
- AWS/GCP: $50-100/月
- ドメイン: $10-15/年
- CDN: $20/月
- **合計: 約$70-120/月**

### エンタープライズ構成
- AWS/GCP (冗長構成): $300-500/月
- 専用DB: $100-200/月
- CDN/WAF: $100/月
- **合計: 約$500-800/月**

## 🚨 重要な注意事項

1. **法的要件**
   - 金融サービスに関する法規制を確認
   - 利用規約・プライバシーポリシーの作成
   - データ保護規制（GDPR等）への対応

2. **セキュリティ対策**
   - 定期的なセキュリティアップデート
   - ペネトレーションテストの実施
   - インシデント対応計画の策定

3. **パフォーマンス最適化**
   - CDNの利用
   - データベースインデックスの最適化
   - キャッシュ戦略の実装

## 📞 サポート

デプロイで困った場合:
1. エラーログを確認: `docker-compose logs`
2. [GitHub Issues](https://github.com/your-repo/issues)で質問
3. 商用サポートの検討

---

**次のステップ**: 
1. デプロイ方法を選択
2. 必要なアカウント/サービスを契約
3. このガイドに従ってデプロイ実行