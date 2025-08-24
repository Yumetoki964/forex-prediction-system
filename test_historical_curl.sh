#!/bin/bash

# ログインしてトークンを取得
echo "=== ログイン ==="
TOKEN=$(curl -s -X POST "http://localhost:8174/api/auth/login" \
  -H "Content-Type: application/json" \
  -d '{"username": "admin", "password": "password"}' | \
  python3 -c "import sys, json; print(json.load(sys.stdin)['access_token'])")

echo "Token取得成功"

# サポートされている通貨ペアを取得
echo -e "\n=== サポートされている通貨ペア ==="
curl -s -X GET "http://localhost:8174/api/historical-data/supported-pairs" \
  -H "Authorization: Bearer $TOKEN" | python3 -m json.tool

# USD/JPYの過去データを取得 (URLエンコード)
echo -e "\n=== USD/JPYの過去データ取得 (3ヶ月) ==="
curl -s -X POST "http://localhost:8174/api/historical-data/fetch/USD%2FJPY?period=3mo" \
  -H "Authorization: Bearer $TOKEN" | python3 -m json.tool

# データサマリーを取得
echo -e "\n=== データサマリー ==="
curl -s -X GET "http://localhost:8174/api/historical-data/summary" \
  -H "Authorization: Bearer $TOKEN" | python3 -m json.tool