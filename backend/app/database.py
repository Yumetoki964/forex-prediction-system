"""
Database configuration and session management
"""

import os
from typing import AsyncGenerator, Generator
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session

# .env.localファイルを読み込む
load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), "..", "..", ".env.local"))

# 環境変数からデータベースURLを取得
DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    raise ValueError("DATABASE_URL environment variable is not set")

# 非同期用のデータベースURL
ASYNC_DATABASE_URL = DATABASE_URL.replace("postgresql://", "postgresql+asyncpg://")

# SQLAlchemyエンジンとセッション設定（同期版）
engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True,  # 接続確認
    pool_recycle=3600,   # 1時間でコネクションプールをリサイクル
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# 非同期SQLAlchemyエンジンとセッション設定
async_engine = create_async_engine(
    ASYNC_DATABASE_URL,
    pool_pre_ping=True,
    pool_recycle=3600,
    echo=False  # SQLログを抑制
)

AsyncSessionLocal = sessionmaker(
    bind=async_engine,
    class_=AsyncSession,
    autocommit=False,
    autoflush=False,
)

Base = declarative_base()


def get_db() -> Generator[Session, None, None]:
    """
    Database session dependency (同期版)
    FastAPIの依存性注入で使用されるデータベースセッション
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


async def get_async_db() -> AsyncGenerator[AsyncSession, None]:
    """
    Async database session dependency (非同期版)
    非同期処理用のデータベースセッション
    """
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()