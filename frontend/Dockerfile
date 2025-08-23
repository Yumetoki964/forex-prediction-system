# React + Vite Frontend Dockerfile
FROM node:18-alpine AS builder

# 作業ディレクトリの設定
WORKDIR /app

# package.jsonとpackage-lock.jsonをコピー
COPY package*.json ./

# 依存関係のインストール
RUN npm ci --only=production

# ソースコードをコピー
COPY . .

# 環境変数ファイルのコピー（ビルド時に使用）
ARG NODE_ENV=production
ENV NODE_ENV=$NODE_ENV

# TypeScriptコンパイルとビルド
RUN npm run build

# Production用のNginxステージ
FROM nginx:alpine

# Nginxの設定をコピー
COPY --from=builder /app/dist /usr/share/nginx/html
COPY nginx.conf /etc/nginx/nginx.conf

# ヘルスチェック
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:80 || exit 1

# ポートの公開
EXPOSE 80

# 実行コマンド
CMD ["nginx", "-g", "daemon off;"]