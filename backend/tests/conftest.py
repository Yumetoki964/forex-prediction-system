"""
Test configuration for forex prediction system
テストの共通設定と実データベース接続
"""

import asyncio
import pytest
import os
from typing import AsyncGenerator
from dotenv import load_dotenv
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import AsyncSessionLocal, async_engine
from app.models import Base

# .env.localを読み込む
load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), "..", "..", ".env.local"))

@pytest.fixture(scope="session")
def event_loop():
    """
    セッションスコープのイベントループ
    非同期テスト用
    """
    try:
        loop = asyncio.get_running_loop()
    except RuntimeError:
        loop = asyncio.new_event_loop()
    yield loop
    loop.close()

@pytest.fixture(scope="session")
async def setup_database():
    """
    データベースのセットアップ
    テストテーブルの作成（既存のテーブルは変更せず）
    """
    async with async_engine.begin() as conn:
        # テーブルが存在しない場合のみ作成
        await conn.run_sync(Base.metadata.create_all)
    yield
    # テスト後のクリーンアップは行わない（実データ主義）

@pytest.fixture
async def db_session(setup_database) -> AsyncSession:
    """
    テスト用データベースセッション
    実データベースを使用
    """
    session = AsyncSessionLocal()
    try:
        yield session
    finally:
        # トランザクションロールバックを行い、テスト後のクリーンアップ
        await session.rollback()
        await session.close()

@pytest.fixture
def anyio_backend():
    """
    anyio使用時のバックエンド指定
    """
    return "asyncio"