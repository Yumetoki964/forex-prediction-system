#!/usr/bin/env python3
"""
過去データ取得APIのテストスクリプト
"""
import requests
import json
from datetime import datetime

BASE_URL = "http://localhost:8174"

def login():
    """ログインしてアクセストークンを取得"""
    login_data = {
        "username": "admin",
        "password": "password"
    }
    
    response = requests.post(f"{BASE_URL}/api/auth/login", json=login_data)
    if response.status_code == 200:
        data = response.json()
        return data["access_token"]
    else:
        print(f"Login failed: {response.status_code}")
        print(response.text)
        return None

def test_supported_pairs(token):
    """サポートされている通貨ペアを取得"""
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(f"{BASE_URL}/api/historical-data/supported-pairs", headers=headers)
    
    print("\n=== Supported Currency Pairs ===")
    if response.status_code == 200:
        data = response.json()
        print(f"Total: {data['count']} pairs")
        for pair in data['supported_pairs']:
            print(f"  - {pair}")
    else:
        print(f"Error: {response.status_code}")
        print(response.text)

def test_fetch_historical_data(token):
    """USD/JPYの過去データを取得"""
    headers = {"Authorization": f"Bearer {token}"}
    params = {"period": "3mo"}  # 3ヶ月分のデータを取得
    
    print("\n=== Fetching USD/JPY Historical Data (3 months) ===")
    # URLパスに直接スラッシュを使用
    response = requests.post(
        f"{BASE_URL}/api/historical-data/fetch/USD/JPY",
        headers=headers,
        params=params
    )
    
    if response.status_code == 200:
        data = response.json()
        print(f"Status: {data['status']}")
        print(f"Message: {data['message']}")
        print(f"Records fetched: {data['records_fetched']}")
        print(f"Records saved: {data['records_saved']}")
        if 'date_range' in data:
            print(f"Date range: {data['date_range']['start']} to {data['date_range']['end']}")
    else:
        print(f"Error: {response.status_code}")
        print(response.text)

def test_data_summary(token):
    """保存されたデータのサマリーを取得"""
    headers = {"Authorization": f"Bearer {token}"}
    
    print("\n=== Data Summary ===")
    response = requests.get(f"{BASE_URL}/api/historical-data/summary", headers=headers)
    
    if response.status_code == 200:
        data = response.json()
        print(f"Total records: {data['total_records']}")
        for pair_info in data['currency_pairs']:
            print(f"\n{pair_info['pair']}:")
            print(f"  Count: {pair_info['count']}")
            print(f"  Date range: {pair_info['date_range']['start']} to {pair_info['date_range']['end']}")
    else:
        print(f"Error: {response.status_code}")
        print(response.text)

def main():
    print("=" * 50)
    print("Historical Data API Test")
    print("=" * 50)
    
    # ログイン
    print("\nLogging in...")
    token = login()
    if not token:
        print("Failed to login")
        return
    
    print("Login successful!")
    
    # テスト実行
    test_supported_pairs(token)
    test_fetch_historical_data(token)
    test_data_summary(token)
    
    print("\n" + "=" * 50)
    print("Test completed!")

if __name__ == "__main__":
    main()