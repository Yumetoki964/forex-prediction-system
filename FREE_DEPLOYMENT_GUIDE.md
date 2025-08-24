# 🆓 完全無料デプロイメントガイド

**推定作業時間**: 30-45分  
**必要なもの**: GitHubアカウント、メールアドレス

## 🚀 デプロイ手順

### **STEP 1: Supabaseでデータベース作成**

1. **Supabaseアカウント作成**
   ```
   https://supabase.com → "Start your project"
   ```

2. **新プロジェクト作成**
   - Organization: "Personal"
   - Project name: "forex-prediction-db"
   - Database Password: 強力なパスワードを設定（メモしておく）
   - Region: Northeast Asia (Tokyo)

3. **データベース情報を取得**
   - Project Settings → Database → Connection string
   - URI形式をコピー: `postgresql://postgres:[YOUR-PASSWORD]@db.[YOUR-REF].supabase.co:5432/postgres`

4. **初期テーブル作成**
   - SQL Editor → New query
   - 以下のSQLを実行:

```sql
-- Users table
CREATE TABLE IF NOT EXISTS users (
    id SERIAL PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    full_name VARCHAR(100),
    role VARCHAR(20) DEFAULT 'user',
    is_active BOOLEAN DEFAULT true,
    is_verified BOOLEAN DEFAULT false,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Exchange rates table
CREATE TABLE IF NOT EXISTS exchange_rates (
    id SERIAL PRIMARY KEY,
    currency_pair VARCHAR(10) DEFAULT 'USD/JPY',
    date DATE NOT NULL,
    open_rate DECIMAL(10, 4),
    high_rate DECIMAL(10, 4),
    low_rate DECIMAL(10, 4),
    close_rate DECIMAL(10, 4) NOT NULL,
    volume BIGINT,
    source VARCHAR(50),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(currency_pair, date, source)
);

-- Default admin user (password: password)
INSERT INTO users (username, email, password_hash, full_name, role, is_active, is_verified)
VALUES (
    'admin',
    'admin@forex.com',
    '$2b$12$LQYeVPIvLBqVGzLPep6o8OgGKvJLeGGfFpS1sC7OKQqWXxQJKvGDu',
    'System Administrator',
    'admin',
    true,
    true
) ON CONFLICT (username) DO NOTHING;
```

### **STEP 2: GitHubリポジトリ作成**

1. **GitHubで新リポジトリ作成**
   ```
   https://github.com/new
   ```
   - Repository name: "forex-prediction-system"
   - Public
   - "Create repository"

2. **ローカルからプッシュ**
```bash
cd /Users/yumetokicross/Desktop/forex-prediction-system

# Git初期化（まだの場合）
git init
git add .
git commit -m "Initial commit: Forex Prediction System"

# リモート追加
git remote add origin https://github.com/[YOUR-USERNAME]/forex-prediction-system.git
git branch -M main
git push -u origin main
```

### **STEP 3: Renderでバックエンドデプロイ**

1. **Renderアカウント作成**
   ```
   https://render.com → "Get Started"
   ```
   - GitHubアカウントでサインアップ

2. **新Webサービス作成**
   - Dashboard → "New +" → "Web Service"
   - "Connect a repository" → 作成したリポジトリを選択
   - 設定:
     - Name: `forex-prediction-backend`
     - Root Directory: `backend`
     - Runtime: `Docker`
     - Dockerfile Path: `Dockerfile.render`
     - Plan: **Free**

3. **環境変数設定**
   - Environment タブで以下を設定:
   ```
   DATABASE_URL = [Supabaseから取得したURI]
   SECRET_KEY = your-very-long-random-secret-key-123456789
   JWT_SECRET_KEY = your-jwt-secret-key-987654321
   ENVIRONMENT = production
   DEBUG = false
   ```

4. **デプロイ実行**
   - "Create Web Service" → 自動でデプロイ開始
   - 5-10分でデプロイ完了

### **STEP 4: Vercelでフロントエンドデプロイ**

1. **Vercelアカウント作成**
   ```
   https://vercel.com → "Start Deploying"
   ```
   - GitHubアカウントでサインアップ

2. **プロジェクトインポート**
   - "New Project" → GitHubリポジトリを選択
   - 設定:
     - Framework Preset: "Vite"
     - Root Directory: `frontend`
     - Build Command: `npm run build`
     - Output Directory: `dist`

3. **環境変数設定**
   - Project Settings → Environment Variables
   ```
   VITE_API_URL = https://[YOUR-RENDER-SERVICE].onrender.com
   ```
   ※ RenderのサービスURLは `https://forex-prediction-backend.onrender.com` 形式

4. **デプロイ実行**
   - "Deploy" → 2-3分でデプロイ完了

### **STEP 5: 動作確認**

1. **フロントエンドURL確認**
   - Vercel Dashboard → Domains → `https://[YOUR-APP].vercel.app`

2. **ログインテスト**
   - Username: `admin`
   - Password: `password`

3. **APIテスト**
   - バックエンドURL: `https://[YOUR-RENDER-SERVICE].onrender.com/docs`

## ⚠️ 重要な制限事項

### **Render無料プランの制限**
- **750時間/月** のサービス稼働時間
- **15分間無アクセスでスリープ**
- 最初のアクセスで起動に30秒程度かかる

### **Supabase無料プランの制限**
- **500MB** のデータベース容量
- **2つの同時接続**
- 1週間のアイドル後にプロジェクト一時停止

### **Vercel無料プランの制限**
- **100GB** の帯域幅/月
- 商用利用の場合は有料プラン推奨

## 🔧 設定完了後のカスタマイズ

### **独自ドメイン設定（オプション）**
1. **無料ドメイン取得**
   - Freenom: .tk, .ml, .ga ドメイン無料

2. **Vercel設定**
   - Project Settings → Domains → Add Domain

### **セキュリティ強化**
1. **パスワード変更**
   - 管理者ログイン後、設定画面でパスワード変更

2. **CORS設定の調整**
   - 本番URLに合わせてCORS設定を更新

### **監視設定**
1. **UptimeRobot**（無料）
   ```
   https://uptimerobot.com
   ```
   - サイトの死活監視
   - ダウン時のメール通知

## 🎯 完了！

✅ フロントエンド: `https://[YOUR-APP].vercel.app`  
✅ バックエンド: `https://[YOUR-RENDER-SERVICE].onrender.com`  
✅ 完全無料での運用開始

---

**次回のアクセス時の注意**:
- Renderサービスは15分無アクセスでスリープするため、初回アクセス時に30秒程度お待ちください
- 月750時間の制限があるため、不要時はRender Dashboardでサービスを一時停止も可能