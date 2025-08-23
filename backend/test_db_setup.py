"""
Database setup script for testing
データベース接続とサンプルデータの作成
"""

import asyncio
import os
from datetime import datetime, timedelta
from decimal import Decimal
from dotenv import load_dotenv
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker, Session

# .env.localファイルを読み込む（プロジェクトルートから）
load_dotenv(dotenv_path="../.env.local")

from app.models import Base, DataSource
from app.schemas.sources import DataSourceTypeEnum, DataSourceStatusEnum

# 環境変数からデータベースURLを取得
DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    raise ValueError("DATABASE_URL environment variable is not set")

print(f"データベースURL: {DATABASE_URL}")

# 同期SQLAlchemyエンジンでテーブル作成
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def setup_database():
    """データベースのセットアップとサンプルデータ作成"""
    
    print("テーブル作成中...")
    
    # テーブル作成
    Base.metadata.create_all(bind=engine)
    print("✅ テーブル作成完了")
    
    # サンプルデータ作成
    db = SessionLocal()
    
    try:
        # 既存データのクリア
        db.query(DataSource).delete()
        
        current_time = datetime.now()
        
        # サンプルデータソース作成
        sample_sources = [
            DataSource(
                name="Yahoo Finance",
                source_type=DataSourceTypeEnum.YAHOO_FINANCE,
                url="https://finance.yahoo.com/quote/USDJPY=X/",
                status=DataSourceStatusEnum.ACTIVE,
                priority=1,
                success_rate=Decimal('0.95'),
                avg_response_time=1200,
                last_success_at=current_time - timedelta(minutes=5),
                failure_count=0,
                daily_request_count=145,
                last_request_at=current_time - timedelta(minutes=5),
            ),
            DataSource(
                name="BOJ CSV",
                source_type=DataSourceTypeEnum.BOJ_CSV,
                url="https://www.boj.or.jp/statistics/market/forex/fxdaily/index.htm/",
                status=DataSourceStatusEnum.ACTIVE,
                priority=2,
                success_rate=Decimal('0.98'),
                avg_response_time=2500,
                last_success_at=current_time - timedelta(hours=1),
                failure_count=0,
                daily_request_count=12,
                last_request_at=current_time - timedelta(hours=1),
            ),
            DataSource(
                name="Alpha Vantage",
                source_type=DataSourceTypeEnum.ALPHA_VANTAGE,
                url="https://www.alphavantage.co/query",
                api_key="demo",
                status=DataSourceStatusEnum.ACTIVE,
                priority=3,
                success_rate=Decimal('0.88'),
                avg_response_time=3200,
                last_success_at=current_time - timedelta(minutes=30),
                last_failure_at=current_time - timedelta(hours=2),
                failure_count=2,
                daily_request_count=89,
                rate_limit_requests=500,
                rate_limit_period=86400,
                last_request_at=current_time - timedelta(minutes=30),
            ),
            DataSource(
                name="Web Scraping Backup",
                source_type=DataSourceTypeEnum.SCRAPING,
                url="https://example.com/forex-data",
                status=DataSourceStatusEnum.ERROR,
                priority=4,
                success_rate=Decimal('0.45'),
                avg_response_time=8500,
                last_success_at=current_time - timedelta(hours=6),
                last_failure_at=current_time - timedelta(minutes=15),
                failure_count=12,
                daily_request_count=25,
                last_request_at=current_time - timedelta(minutes=15),
            )
        ]
        
        for source in sample_sources:
            db.add(source)
        
        db.commit()
        
        # データ確認
        count = db.query(DataSource).count()
        print(f"✅ サンプルデータ作成完了: {count}件のデータソース")
        
        # 作成されたデータの確認
        sources = db.query(DataSource).all()
        for source in sources:
            print(f"  - {source.name} ({source.source_type.value}) - {source.status.value}")
        
    except Exception as e:
        db.rollback()
        print(f"❌ エラー発生: {e}")
        raise
    finally:
        db.close()

def test_database_connection():
    """データベース接続テスト"""
    try:
        db = SessionLocal()
        result = db.execute(text("SELECT 1 as test"))
        test_value = result.scalar()
        db.close()
        
        if test_value == 1:
            print("✅ データベース接続テスト成功")
            return True
        else:
            print("❌ データベース接続テスト失敗")
            return False
            
    except Exception as e:
        print(f"❌ データベース接続エラー: {e}")
        return False

if __name__ == "__main__":
    print("=== データベースセットアップ開始 ===")
    
    # 接続テスト
    if test_database_connection():
        # セットアップ実行
        setup_database()
        print("=== データベースセットアップ完了 ===")
    else:
        print("データベース接続に失敗しました。PostgreSQLが起動しているか確認してください。")
        print("Docker起動コマンド: docker run --name postgres -e POSTGRES_PASSWORD=postgres -p 5432:5432 -d postgres")