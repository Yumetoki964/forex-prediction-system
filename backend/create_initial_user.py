"""
初期ユーザー作成スクリプト
管理者ユーザーと一般ユーザーを作成
"""

import asyncio
import os
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# 環境変数読み込み
load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), "..", ".env.local"))

from app.models import User, UserRole
from app.core.auth import get_password_hash


def create_initial_users():
    """初期ユーザーを作成"""
    
    # データベース接続
    DATABASE_URL = os.getenv("DATABASE_URL")
    if not DATABASE_URL:
        raise ValueError("DATABASE_URL environment variable is not set")
    
    engine = create_engine(DATABASE_URL)
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    
    with SessionLocal() as db:
        # 既存ユーザーチェック
        existing_users = db.query(User).count()
        if existing_users > 0:
            print(f"既に {existing_users} ユーザーが存在します。初期ユーザーの作成をスキップします。")
            return
        
        # 管理者ユーザー作成
        admin_user = User(
            username="admin",
            email="admin@forex-prediction.local",
            hashed_password=get_password_hash("password"),
            full_name="System Administrator",
            role=UserRole.ADMIN,
            is_active=True,
            is_verified=True,
            failed_login_attempts=0
        )
        db.add(admin_user)
        
        # 一般ユーザー作成
        regular_user = User(
            username="user",
            email="user@forex-prediction.local",
            hashed_password=get_password_hash("password"),
            full_name="Test User",
            role=UserRole.USER,
            is_active=True,
            is_verified=True,
            failed_login_attempts=0
        )
        db.add(regular_user)
        
        # コミット
        db.commit()
        
        print("初期ユーザーが作成されました:")
        print("- 管理者: admin / password")
        print("- 一般ユーザー: user / password")


if __name__ == "__main__":
    create_initial_users()