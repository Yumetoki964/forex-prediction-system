# FastAPI Backend Dockerfile
FROM python:3.11-slim

# 作業ディレクトリの設定
WORKDIR /app

# システム依存関係のインストール
RUN apt-get update && apt-get install -y \
    gcc \
    postgresql-client \
    curl \
    && rm -rf /var/lib/apt/lists/*

# requirements.txtを作成（アプリケーションの依存関係）
COPY requirements.txt* ./
RUN if [ ! -f requirements.txt ]; then \
    echo "fastapi==0.104.1" > requirements.txt && \
    echo "uvicorn[standard]==0.24.0" >> requirements.txt && \
    echo "sqlalchemy==2.0.23" >> requirements.txt && \
    echo "psycopg2-binary==2.9.9" >> requirements.txt && \
    echo "pandas==2.1.4" >> requirements.txt && \
    echo "numpy==1.25.2" >> requirements.txt && \
    echo "scikit-learn==1.3.2" >> requirements.txt && \
    echo "pydantic==2.5.0" >> requirements.txt && \
    echo "python-multipart==0.0.6" >> requirements.txt && \
    echo "python-dotenv==1.0.0" >> requirements.txt && \
    echo "alembic==1.13.1" >> requirements.txt && \
    echo "asyncpg==0.29.0" >> requirements.txt && \
    echo "httpx==0.25.2" >> requirements.txt && \
    echo "beautifulsoup4==4.12.2" >> requirements.txt && \
    echo "requests==2.31.0" >> requirements.txt; \
fi

# 依存関係のインストール
RUN pip install --no-cache-dir -r requirements.txt

# アプリケーションファイルをコピー
COPY . .

# モデルディレクトリの作成
RUN mkdir -p models logs

# ヘルスチェック
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:$API_PORT/docs || exit 1

# ポートの公開
EXPOSE 8080

# 実行コマンド
CMD ["python", "-m", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8080"]