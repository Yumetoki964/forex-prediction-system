#!/usr/bin/env python3
"""
デモユーザーを作成するスクリプト（データベース不要版）
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.core.auth import get_password_hash

# メモリ内にデモユーザーを作成
demo_users = {
    "admin": {
        "username": "admin",
        "email": "admin@example.com",
        "full_name": "Admin User",
        "hashed_password": get_password_hash("password"),
        "role": "admin",
        "is_active": True
    },
    "user": {
        "username": "user", 
        "email": "user@example.com",
        "full_name": "Demo User",
        "hashed_password": get_password_hash("password"),
        "role": "user",
        "is_active": True
    }
}

print("✅ デモユーザー情報:")
print("- admin / password (管理者)")
print("- user / password (一般ユーザー)")
print("\nこれらのユーザーはメモリ内に作成されました。")