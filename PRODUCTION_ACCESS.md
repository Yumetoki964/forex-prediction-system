# 🎉 本番環境デプロイ完了！

## 📱 アクセス情報

### 現在の本番環境

本番環境が以下のポートで稼働しています：

- **フロントエンド**: http://localhost:3000
- **バックエンドAPI**: http://localhost:8000
- **APIドキュメント**: http://localhost:8000/docs

### ログイン情報

以下の認証情報でログインできます：

**管理者アカウント:**
- ユーザー名: `admin`
- パスワード: `password`

**一般ユーザーアカウント:**
- ユーザー名: `user`
- パスワード: `password`

## 🔍 動作確認

### 1. フロントエンドへアクセス
ブラウザで http://localhost:3000 を開いてください。

### 2. ログイン
上記の認証情報でログインしてください。

### 3. ダッシュボード確認
ログイン後、為替予測ダッシュボードが表示されます。

## 🛠️ サービス管理

### サービスの状態確認

```bash
# フロントエンドのログ確認
ps aux | grep serve

# バックエンドのログ確認
ps aux | grep uvicorn

# ヘルスチェック
curl http://localhost:8000/api/health
```

### サービスの停止

現在のターミナルセッションを終了するか、以下のコマンドを実行：

```bash
# プロセスIDを確認
ps aux | grep serve
ps aux | grep uvicorn

# プロセスを停止
kill <PID>
```

### サービスの再起動

```bash
# フロントエンド再起動
serve -s /Users/yumetokicross/Desktop/forex-prediction-system/frontend/dist -l 3000 &

# バックエンド再起動
cd /Users/yumetokicross/Desktop/forex-prediction-system/backend
python3 -m uvicorn app.main:app --host 0.0.0.0 --port 8000 &
```

## 📊 本番環境の特徴

1. **最適化されたビルド**
   - Reactアプリケーションが本番用に最適化
   - ファイルサイズの最小化
   - 高速な読み込み

2. **パフォーマンス**
   - gzip圧縮
   - 静的ファイルの効率的な配信
   - APIレスポンスの高速化

3. **セキュリティ**
   - CORS設定
   - セキュリティヘッダー
   - 本番用の設定

## 🐛 トラブルシューティング

### ポートが使用中の場合

```bash
# 使用中のポートを確認
lsof -i :3000
lsof -i :8000

# 必要に応じてプロセスを停止
kill -9 <PID>
```

### ログインできない場合

1. バックエンドが起動しているか確認
2. フロントエンドのコンソールでエラーを確認
3. ネットワークタブでAPIリクエストを確認

### APIエラーが表示される場合

一部のAPIエンドポイントはまだ実装されていないため、404エラーが表示されることがあります。
これは正常な動作です。

## 📝 次のステップ

### クラウドデプロイ

本番環境をクラウドにデプロイする場合：

1. **AWS EC2 / Google Cloud / Azure**
   - VMインスタンスを作成
   - Dockerをインストール
   - リポジトリをクローン
   - deploy.shスクリプトを実行

2. **Heroku**
   - Heroku CLIをインストール
   - Procfileを作成
   - git push heroku main

3. **Vercel (フロントエンドのみ)**
   - Vercel CLIをインストール
   - vercel deployを実行

### SSL証明書の設定

本番環境では必ずHTTPSを使用してください：

```bash
# Let's Encryptの例
sudo certbot --nginx -d your-domain.com
```

## 📞 サポート

問題が発生した場合は、以下の情報と共にissueを作成してください：

1. エラーメッセージ
2. ブラウザのコンソールログ
3. ネットワークタブの情報
4. バックエンドのログ

---

**現在の本番環境URL: http://localhost:3000**

お楽しみください！ 🚀