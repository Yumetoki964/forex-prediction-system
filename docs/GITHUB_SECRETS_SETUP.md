# 🔐 GitHub Secrets 設定ガイド

Forex Prediction SystemのCI/CDパイプラインを動作させるために必要なSecretsをGitHubリポジトリに設定します。

## Repository Secrets (全環境共通)

GitHub → Settings → Secrets and variables → Actions → New repository secret:

### 必須Secrets

```bash
# Container Registry
GITHUB_TOKEN                 # 自動設定 (GitHub Actions用)

# デプロイメントプラットフォーム認証
RAILWAY_TOKEN               # Railway CLI token
RENDER_API_KEY              # Render API key

# 外部API (全環境共通)
ALPHA_VANTAGE_API_KEY       # Alpha Vantage API key
OANDA_API_TOKEN             # OANDA API token
OANDA_ACCOUNT_ID            # OANDA account ID
OPENAI_API_KEY              # OpenAI API key (ML機能用)
```

### オプション Secrets

```bash
# セキュリティスキャン
SNYK_TOKEN                  # Snyk security scanning
CODECOV_TOKEN               # Code coverage reporting

# 通知
SLACK_WEBHOOK               # Slack通知用webhook URL
SECURITY_WEBHOOK            # セキュリティアラート用webhook URL
GITLEAKS_LICENSE            # GitLeaks商用ライセンス
```

## Environment Secrets (環境別)

### Staging Environment

GitHub → Settings → Environments → staging → Add secret:

```bash
# ステージング環境URL・API
STAGING_API_URL             # https://staging-api.yourapp.com
STAGING_API_KEY             # ステージング環境用APIキー

# ステージング環境データベース
STAGING_DATABASE_URL        # postgresql://user:pass@host:port/staging_db

# Railway/Render設定 (ステージング)
RAILWAY_PROJECT_ID_STAGING  # Railway project ID (staging)
RENDER_SERVICE_ID_STAGING   # Render service ID (staging)
```

### Production Environment  

GitHub → Settings → Environments → production → Add secret:

```bash
# 本番環境URL・API
PRODUCTION_API_URL          # https://api.yourapp.com
PRODUCTION_API_KEY          # 本番環境用APIキー

# 本番環境データベース
PRODUCTION_DATABASE_URL     # postgresql://user:pass@host:port/prod_db

# Railway/Render設定 (本番)
RAILWAY_PROJECT_ID_PRODUCTION  # Railway project ID (production)
RENDER_SERVICE_ID_PRODUCTION   # Render service ID (production)

# 本番専用セキュリティ
JWT_SECRET_KEY              # JWT署名用秘密鍵 (本番専用)
NEXTAUTH_SECRET             # Next.js認証用秘密鍵 (本番専用)
```

## Repository Variables (公開可能な設定)

GitHub → Settings → Secrets and variables → Actions → Variables:

```bash
# デプロイメント設定
DEPLOYMENT_PLATFORM         # "railway" or "render"
PRODUCTION_URL              # https://yourapp.com
STAGING_URL                 # https://staging.yourapp.com

# コンテナレジストリ
REGISTRY                    # ghcr.io
IMAGE_NAME_PREFIX           # forex-prediction-system
```

## 🚀 一括設定スクリプト

GitHub CLIを使用してSecretsを一括設定:

### 基本設定スクリプト

```bash
#!/bin/bash
# scripts/setup-github-secrets.sh

echo "🔐 GitHub Secrets設定開始..."

# 必要なツールの確認
if ! command -v gh &> /dev/null; then
    echo "❌ GitHub CLI (gh) がインストールされていません"
    echo "インストール: https://cli.github.com/"
    exit 1
fi

# 認証確認
if ! gh auth status &> /dev/null; then
    echo "❌ GitHub CLI認証が必要です"
    echo "認証: gh auth login"
    exit 1
fi

echo "✅ GitHub CLI認証確認済み"

# リポジトリSecretsの設定
echo "📝 Repository Secrets設定中..."

read -p "Railway Token: " RAILWAY_TOKEN
gh secret set RAILWAY_TOKEN --body "$RAILWAY_TOKEN"

read -p "Render API Key (オプション): " RENDER_API_KEY
if [ ! -z "$RENDER_API_KEY" ]; then
    gh secret set RENDER_API_KEY --body "$RENDER_API_KEY"
fi

read -p "Alpha Vantage API Key: " ALPHA_VANTAGE_KEY
gh secret set ALPHA_VANTAGE_API_KEY --body "$ALPHA_VANTAGE_KEY"

read -p "OANDA API Token: " OANDA_TOKEN
gh secret set OANDA_API_TOKEN --body "$OANDA_TOKEN"

read -p "OANDA Account ID: " OANDA_ACCOUNT
gh secret set OANDA_ACCOUNT_ID --body "$OANDA_ACCOUNT"

read -p "OpenAI API Key: " OPENAI_KEY
gh secret set OPENAI_API_KEY --body "$OPENAI_KEY"

echo "✅ Repository Secrets設定完了"

# Variables設定
echo "📝 Repository Variables設定中..."

gh variable set DEPLOYMENT_PLATFORM --body "railway"
gh variable set REGISTRY --body "ghcr.io"
gh variable set IMAGE_NAME_PREFIX --body "forex-prediction-system"

echo "✅ Repository Variables設定完了"

# ステージング環境Secrets
echo "📝 Staging Environment Secrets設定中..."

read -p "Staging API URL: " STAGING_API_URL
gh secret set STAGING_API_URL --env staging --body "$STAGING_API_URL"

read -p "Staging Database URL: " STAGING_DB_URL
gh secret set STAGING_DATABASE_URL --env staging --body "$STAGING_DB_URL"

read -p "Staging API Key: " STAGING_API_KEY
gh secret set STAGING_API_KEY --env staging --body "$STAGING_API_KEY"

echo "✅ Staging Environment Secrets設定完了"

# 本番環境Secrets
echo "📝 Production Environment Secrets設定中..."

read -p "Production API URL: " PRODUCTION_API_URL
gh secret set PRODUCTION_API_URL --env production --body "$PRODUCTION_API_URL"

read -p "Production Database URL: " PRODUCTION_DB_URL
gh secret set PRODUCTION_DATABASE_URL --env production --body "$PRODUCTION_DB_URL"

read -p "Production API Key: " PRODUCTION_API_KEY
gh secret set PRODUCTION_API_KEY --env production --body "$PRODUCTION_API_KEY"

# 本番用ランダムシークレット生成
echo "🔑 本番用セキュリティキー生成中..."
JWT_SECRET=$(openssl rand -base64 32)
NEXTAUTH_SECRET=$(openssl rand -base64 32)

gh secret set JWT_SECRET_KEY --env production --body "$JWT_SECRET"
gh secret set NEXTAUTH_SECRET --env production --body "$NEXTAUTH_SECRET"

echo "✅ Production Environment Secrets設定完了"

# Variables設定 (環境URL)
gh variable set PRODUCTION_URL --body "$PRODUCTION_API_URL"
gh variable set STAGING_URL --body "$STAGING_API_URL"

echo "🎉 全ての設定が完了しました！"

# 設定確認
echo "📋 設定されたSecretsの確認:"
gh secret list
echo ""
echo "📋 Staging Environment:"
gh secret list --env staging
echo ""
echo "📋 Production Environment:"  
gh secret list --env production
echo ""
echo "📋 Variables:"
gh variable list
```

### 簡易設定版

```bash
#!/bin/bash
# scripts/setup-basic-secrets.sh

echo "🔐 基本的なGitHub Secrets設定..."

# 外部API設定のみ (最小限)
gh secret set ALPHA_VANTAGE_API_KEY --body "your_alpha_vantage_key"
gh secret set OANDA_API_TOKEN --body "your_oanda_token"
gh secret set OANDA_ACCOUNT_ID --body "your_oanda_account"

# デプロイメント設定
gh secret set RAILWAY_TOKEN --body "your_railway_token"

# 本番用セキュリティキー
gh secret set JWT_SECRET_KEY --env production --body "$(openssl rand -base64 32)"

echo "✅ 基本設定完了"
```

## 🔍 設定確認コマンド

```bash
# 全Secretsの確認
gh secret list

# 環境別Secretsの確認
gh secret list --env staging
gh secret list --env production

# Variablesの確認
gh variable list

# 特定のSecretの存在確認
gh secret list | grep -i "RAILWAY_TOKEN"
```

## 🔧 トラブルシューティング

### 1. GitHub CLI認証エラー

```bash
# 認証状態確認
gh auth status

# 再認証
gh auth login

# トークンでの認証
gh auth login --with-token < your-token.txt
```

### 2. Secret設定エラー

```bash
# Secret削除 (設定し直し)
gh secret delete SECRET_NAME

# Environment Secret削除
gh secret delete SECRET_NAME --env production
```

### 3. 権限エラー

- リポジトリの管理者権限が必要
- Organization リポジトリの場合は追加の権限設定が必要

## 📋 設定チェックリスト

### Repository Secrets
- [ ] RAILWAY_TOKEN
- [ ] ALPHA_VANTAGE_API_KEY  
- [ ] OANDA_API_TOKEN
- [ ] OANDA_ACCOUNT_ID
- [ ] OPENAI_API_KEY

### Staging Environment
- [ ] STAGING_API_URL
- [ ] STAGING_DATABASE_URL
- [ ] STAGING_API_KEY

### Production Environment
- [ ] PRODUCTION_API_URL
- [ ] PRODUCTION_DATABASE_URL
- [ ] PRODUCTION_API_KEY
- [ ] JWT_SECRET_KEY
- [ ] NEXTAUTH_SECRET

### Repository Variables
- [ ] DEPLOYMENT_PLATFORM
- [ ] PRODUCTION_URL
- [ ] STAGING_URL

## 🔒 セキュリティのベストプラクティス

### 1. Secret管理
- 最小権限の原則
- 定期的なローテーション
- 本番・ステージング環境の分離

### 2. アクセス制御
- Environment保護ルール設定
- 必須レビュー者の設定
- ブランチ制限

### 3. 監査
- Secret使用状況の定期確認
- アクセスログの確認
- 不要なSecretの削除

---

## 🆘 サポート

設定で問題が発生した場合:

1. **GitHub CLI エラー**: [GitHub CLI docs](https://cli.github.com/manual/)
2. **Secret設定エラー**: GitHub リポジトリの Settings → Secrets で手動設定
3. **権限エラー**: リポジトリ管理者に相談

設定完了後は、GitHub Actions の最初のワークフロー実行で全ての設定が正常に動作することを確認してください。