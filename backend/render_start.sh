#!/bin/bash
# Render.com起動スクリプト

echo "Starting Forex Prediction Backend..."

# ポート設定（Renderは$PORT環境変数を自動設定）
PORT=${PORT:-8000}

# データベース接続テスト
echo "Testing database connection..."
python -c "
import os
from sqlalchemy import create_engine
try:
    engine = create_engine(os.environ.get('DATABASE_URL', ''))
    conn = engine.connect()
    conn.close()
    print('Database connection successful')
except Exception as e:
    print(f'Database connection failed: {e}')
"

# アプリケーション起動
echo "Starting Gunicorn on port $PORT..."
exec gunicorn app.main:app \
    --workers 1 \
    --worker-class uvicorn.workers.UvicornWorker \
    --bind 0.0.0.0:$PORT \
    --timeout 120 \
    --access-logfile - \
    --error-logfile - \
    --log-level info