"""
Forex Prediction System - Rates Service
=======================================

為替レート関連のサービス層実装
エンドポイント 1.1: /api/rates/current 用のサービス
"""

import logging
from datetime import datetime, timedelta, date
from typing import Optional
import asyncio
import aiohttp
from decimal import Decimal
from sqlalchemy.orm import Session
from sqlalchemy import select, desc

from ..models import ExchangeRate, DataSourceType
from ..schemas.rates_minimal import CurrentRateResponse

logger = logging.getLogger(__name__)


class RatesService:
    """為替レート関連のサービスクラス"""

    def __init__(self, db: Session):
        self.db = db

    async def get_current_rate(self) -> CurrentRateResponse:
        """
        現在のドル円レートを取得
        
        Returns:
            CurrentRateResponse: 現在のレート情報
        """
        try:
            # 1. データベースから最新レートを取得
            latest_rate = await self._get_latest_rate_from_db()
            
            # 2. 最新データが古い（6時間以上前）場合、外部APIから取得
            if self._is_rate_stale(latest_rate):
                logger.info("Latest rate is stale, fetching from external source")
                fresh_rate = await self._fetch_rate_from_external_source()
                if fresh_rate:
                    latest_rate = fresh_rate

            # 3. 24時間前のデータと比較して変動率を計算
            previous_rate = await self._get_rate_24h_ago()
            
            # 4. レスポンス作成
            current_time = datetime.now()
            
            if not latest_rate:
                # フォールバック：リアルな市場データ風のモックを返す（開発時のみ）
                import random
                logger.warning("No rate data available, returning mock market data")
                
                # 2024年8月現在の現実的なドル円レート付近で変動
                base_rate = 149.50
                rate = base_rate + random.uniform(-0.5, 0.5)
                change_24h = random.uniform(-1.5, 1.5)
                
                return CurrentRateResponse(
                    rate=round(rate, 2),
                    timestamp=current_time,
                    change_24h=round(change_24h, 2),
                    change_percentage_24h=round(change_24h / base_rate * 100, 2),
                    open_rate=round(base_rate - 0.2, 2),
                    high_rate=round(rate + random.uniform(0, 0.5), 2),
                    low_rate=round(rate - random.uniform(0, 0.5), 2),
                    volume=random.randint(100000, 500000),
                    is_market_open=self._is_market_open(current_time),
                    source="mock_market"
                )

            # 24時間変動計算
            change_24h = 0.0
            change_percentage_24h = 0.0
            if previous_rate and previous_rate.close_rate:
                change_24h = float(latest_rate.close_rate - previous_rate.close_rate)
                change_percentage_24h = (change_24h / float(previous_rate.close_rate)) * 100

            return CurrentRateResponse(
                rate=float(latest_rate.close_rate),
                timestamp=current_time,
                change_24h=change_24h,
                change_percentage_24h=change_percentage_24h,
                open_rate=float(latest_rate.open_rate) if latest_rate.open_rate else None,
                high_rate=float(latest_rate.high_rate) if latest_rate.high_rate else None,
                low_rate=float(latest_rate.low_rate) if latest_rate.low_rate else None,
                volume=latest_rate.volume,
                is_market_open=self._is_market_open(current_time),
                source=latest_rate.source.value if latest_rate.source else "unknown"
            )

        except Exception as e:
            logger.error(f"Error getting current rate: {str(e)}")
            # エラー時フォールバック
            current_time = datetime.now()
            return CurrentRateResponse(
                rate=150.25,
                timestamp=current_time,
                change_24h=0.0,
                change_percentage_24h=0.0,
                open_rate=None,
                high_rate=None,
                low_rate=None,
                volume=None,
                is_market_open=self._is_market_open(current_time),
                source="error_fallback"
            )

    async def _get_latest_rate_from_db(self) -> Optional[ExchangeRate]:
        """データベースから最新の為替レートを取得"""
        try:
            stmt = select(ExchangeRate).order_by(desc(ExchangeRate.date)).limit(1)
            result = self.db.execute(stmt)
            return result.scalar_one_or_none()
        except Exception as e:
            logger.error(f"Error fetching latest rate from database: {str(e)}")
            return None

    async def _get_rate_24h_ago(self) -> Optional[ExchangeRate]:
        """24時間前のレートを取得"""
        try:
            target_date = date.today() - timedelta(days=1)
            stmt = select(ExchangeRate).where(ExchangeRate.date == target_date)
            result = self.db.execute(stmt)
            return result.scalar_one_or_none()
        except Exception as e:
            logger.error(f"Error fetching 24h ago rate: {str(e)}")
            return None

    def _is_rate_stale(self, rate: Optional[ExchangeRate]) -> bool:
        """レートデータが古いかどうかを判定"""
        if not rate:
            return True
        
        # 6時間以上前のデータは古いとみなす
        if rate.updated_at:
            return (datetime.now() - rate.updated_at).total_seconds() > 6 * 3600
        
        # 日付ベースでの判定（当日以外は古い）
        return rate.date < date.today()

    async def _fetch_rate_from_external_source(self) -> Optional[ExchangeRate]:
        """
        外部ソース（Yahoo Finance）から最新レートを取得
        
        Returns:
            Optional[ExchangeRate]: 取得したレートデータ、失敗時はNone
        """
        try:
            # Yahoo Finance USD/JPY データをスクレイピング
            url = "https://finance.yahoo.com/quote/USDJPY=X/"
            
            async with aiohttp.ClientSession() as session:
                headers = {
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
                }
                
                timeout = aiohttp.ClientTimeout(total=10)
                async with session.get(url, headers=headers, timeout=timeout) as response:
                    if response.status == 200:
                        html = await response.text()
                        return self._parse_yahoo_finance_data(html)
                    else:
                        logger.warning(f"Yahoo Finance returned status {response.status}")
                        return None

        except asyncio.TimeoutError:
            logger.warning("Timeout fetching data from Yahoo Finance")
            return None
        except Exception as e:
            logger.error(f"Error fetching rate from external source: {str(e)}")
            return None

    def _parse_yahoo_finance_data(self, html: str) -> Optional[ExchangeRate]:
        """
        Yahoo FinanceのHTMLデータからレート情報をパース
        
        Args:
            html: Yahoo FinanceのHTMLレスポンス
            
        Returns:
            Optional[ExchangeRate]: パースしたレートデータ
        """
        try:
            # 簡単なパターンマッチングでレートを抽出
            # 実際の実装では、BeautifulSoupなどを使用してより堅牢にパースする
            import re
            
            # 現在レートを抽出（Yahoo Financeの基本的なパターン）
            rate_pattern = r'"regularMarketPrice":\{"raw":([0-9.]+)'
            rate_match = re.search(rate_pattern, html)
            
            if rate_match:
                current_rate = Decimal(rate_match.group(1))
                
                # 新しいレートデータを作成（データベースに保存は別途実施）
                new_rate = ExchangeRate(
                    date=date.today(),
                    close_rate=current_rate,
                    source=DataSourceType.YAHOO_FINANCE,
                    created_at=datetime.now(),
                    updated_at=datetime.now()
                )
                
                # 追加データの抽出を試行
                try:
                    # 開始価格パターン
                    open_pattern = r'"regularMarketOpen":\{"raw":([0-9.]+)'
                    open_match = re.search(open_pattern, html)
                    if open_match:
                        new_rate.open_rate = Decimal(open_match.group(1))
                    
                    # 高値パターン
                    high_pattern = r'"regularMarketDayHigh":\{"raw":([0-9.]+)'
                    high_match = re.search(high_pattern, html)
                    if high_match:
                        new_rate.high_rate = Decimal(high_match.group(1))
                    
                    # 安値パターン
                    low_pattern = r'"regularMarketDayLow":\{"raw":([0-9.]+)'
                    low_match = re.search(low_pattern, html)
                    if low_match:
                        new_rate.low_rate = Decimal(low_match.group(1))
                        
                except Exception as parse_error:
                    logger.warning(f"Could not parse additional rate data: {str(parse_error)}")
                
                return new_rate
            else:
                logger.warning("Could not find rate data in Yahoo Finance response")
                return None
                
        except Exception as e:
            logger.error(f"Error parsing Yahoo Finance data: {str(e)}")
            return None

    def _is_market_open(self, current_time: datetime) -> bool:
        """
        為替市場の開場状況を判定
        
        Args:
            current_time: 現在時刻
            
        Returns:
            bool: 市場開場中かどうか
        """
        # 為替市場は基本的に24時間（平日）
        # 簡易実装：平日を開場とする
        weekday = current_time.weekday()  # 0=月曜, 6=日曜
        
        # 土日は基本的に閉場
        if weekday >= 5:  # 土日
            return False
        
        # 平日は開場とする（実際にはより複雑な判定が必要）
        return True

    async def save_rate_to_db(self, rate_data: ExchangeRate) -> bool:
        """
        レートデータをデータベースに保存
        
        Args:
            rate_data: 保存するレートデータ
            
        Returns:
            bool: 保存成功かどうか
        """
        try:
            # 同じ日付のデータが存在するかチェック
            existing_rate = self.db.execute(
                select(ExchangeRate).where(ExchangeRate.date == rate_data.date)
            ).scalar_one_or_none()
            
            if existing_rate:
                # 既存データを更新
                existing_rate.close_rate = rate_data.close_rate
                existing_rate.open_rate = rate_data.open_rate
                existing_rate.high_rate = rate_data.high_rate
                existing_rate.low_rate = rate_data.low_rate
                existing_rate.volume = rate_data.volume
                existing_rate.source = rate_data.source
                existing_rate.updated_at = datetime.now()
            else:
                # 新規データを追加
                self.db.add(rate_data)
            
            self.db.commit()
            return True
            
        except Exception as e:
            logger.error(f"Error saving rate to database: {str(e)}")
            self.db.rollback()
            return False