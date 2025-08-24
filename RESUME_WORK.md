# 作業再開ガイド

## 📊 現在の進捗状況

### ✅ 完了した作業
1. **認証システム** - JWT認証の実装完了
2. **本番環境構築** - Dockerless本番環境の構築完了
3. **APIエンドポイント追加** - alerts, metricsエンドポイント追加
4. **WebSocket実装** - リアルタイムデータ更新のためのWebSocket追加
5. **本番ビルド** - フロントエンドの本番ビルド完了

### 🚧 次の作業
1. データベース連携の実装
2. Docker環境の完全構築
3. クラウドデプロイの準備
4. CI/CDパイプラインの設定

## 🚀 作業を再開する方法

### 1. 開発環境で再開する場合

```bash
# バックエンドを起動（ターミナル1）
cd /Users/yumetokicross/Desktop/forex-prediction-system/backend
python3 -m uvicorn app.main:app --reload --port 8174

# フロントエンドを起動（ターミナル2）
cd /Users/yumetokicross/Desktop/forex-prediction-system/frontend
npm run dev
```

アクセスURL: http://localhost:5173

### 2. 本番環境で再開する場合

```bash
# バックエンドを起動（ターミナル1）
cd /Users/yumetokicross/Desktop/forex-prediction-system/backend
python3 -m uvicorn app.main:app --host 0.0.0.0 --port 8000

# フロントエンドを起動（ターミナル2）
cd /Users/yumetokicross/Desktop/forex-prediction-system/frontend
serve -s dist -l 3000
```

アクセスURL: http://localhost:3000

## 🔐 ログイン情報

- **ユーザー名**: `admin`
- **パスワード**: `password`

または

- **ユーザー名**: `user`
- **パスワード**: `password`

## 📁 重要なファイル

### 設定ファイル
- `/frontend/.env.local` - フロントエンド環境変数
- `/backend/app/main.py` - バックエンドメインファイル
- `/docker-compose.prod.yml` - Docker本番構成

### ドキュメント
- `/DEPLOYMENT.md` - デプロイ手順書
- `/PRODUCTION_ACCESS.md` - 本番環境アクセス情報
- `/docs/SCOPE_PROGRESS.md` - プロジェクト進捗管理

## 🐛 トラブルシューティング

### ポートが使用中の場合
```bash
lsof -i :8174
lsof -i :5173
lsof -i :8000
lsof -i :3000
# 該当プロセスをkill
```

### npm関連のエラー
```bash
cd frontend
rm -rf node_modules package-lock.json
npm install
```

### Python関連のエラー
```bash
cd backend
pip3 install -r requirements.txt
```

## 💡 次回作業時の推奨事項

1. **データベース実装**
   - SQLAlchemyモデルの作成
   - マイグレーション設定
   - 実データの永続化

2. **Docker完全対応**
   - Dockerfileの最適化
   - docker-compose.ymlの調整
   - ボリュームマウントの設定

3. **CI/CD設定**
   - GitHub Actionsの設定
   - 自動テストの追加
   - 自動デプロイの構築

4. **セキュリティ強化**
   - 環境変数の適切な管理
   - HTTPS設定
   - レート制限の実装

---

お疲れ様でした！この情報を参考に、いつでも作業を再開できます。