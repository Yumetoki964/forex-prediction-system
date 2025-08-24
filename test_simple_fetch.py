#!/usr/bin/env python3
"""
シンプルな過去データ取得テスト
"""
import requests
import json

# ログイン
login_data = {"username": "admin", "password": "password"}
login_resp = requests.post("http://localhost:8174/api/auth/login", json=login_data)
token = login_resp.json()["access_token"]
headers = {"Authorization": f"Bearer {token}"}

print("Token取得成功")
print(f"Token: {token[:20]}...")

# USD/JPYデータ取得（スラッシュなし）
print("\n=== USD/JPYデータ取得テスト ===")
resp = requests.post(
    "http://localhost:8174/api/historical-data/fetch/USDJPY",
    headers=headers,
    params={"period": "1mo"}
)
print(f"Status: {resp.status_code}")
if resp.status_code == 200:
    data = resp.json()
    print(json.dumps(data, indent=2))
else:
    print(f"Error: {resp.text}")

# データサマリー
print("\n=== データサマリー ===")
resp = requests.get(
    "http://localhost:8174/api/historical-data/summary",
    headers=headers
)
print(f"Status: {resp.status_code}")
if resp.status_code == 200:
    data = resp.json()
    print(json.dumps(data, indent=2))
else:
    print(f"Error: {resp.text}")