"""
Historical data service for fetching past forex data
"""
import yfinance as yf
import pandas as pd
from datetime import datetime, timedelta, date
from typing import List, Optional, Dict, Any
import asyncio
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_
import logging

from app.models import ExchangeRate, DataSourceType

logger = logging.getLogger(__name__)


class HistoricalDataService:
    """Service for fetching and storing historical forex data"""
    
    SUPPORTED_PAIRS = {
        'USD/JPY': 'USDJPY=X',
        'USDJPY': 'USDJPY=X',  # スラッシュなしもサポート
        'EUR/USD': 'EURUSD=X',
        'EURUSD': 'EURUSD=X',
        'GBP/USD': 'GBPUSD=X',
        'GBPUSD': 'GBPUSD=X',
        'USD/CHF': 'USDCHF=X',
        'USDCHF': 'USDCHF=X',
        'AUD/USD': 'AUDUSD=X',
        'AUDUSD': 'AUDUSD=X',
        'USD/CAD': 'USDCAD=X',
        'USDCAD': 'USDCAD=X',
        'NZD/USD': 'NZDUSD=X',
        'NZDUSD': 'NZDUSD=X',
        'EUR/JPY': 'EURJPY=X',
        'EURJPY': 'EURJPY=X',
        'GBP/JPY': 'GBPJPY=X',
        'GBPJPY': 'GBPJPY=X',
        'EUR/GBP': 'EURGBP=X',
        'EURGBP': 'EURGBP=X'
    }
    
    def __init__(self):
        self.source = DataSourceType.YFINANCE
        
    async def fetch_historical_data(
        self,
        currency_pair: str = 'USD/JPY',
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
        period: str = '1y'
    ) -> pd.DataFrame:
        """
        Fetch historical data for a currency pair
        
        Args:
            currency_pair: Currency pair (e.g., 'USD/JPY')
            start_date: Start date for data fetch
            end_date: End date for data fetch
            period: Period string if dates not specified (1d, 5d, 1mo, 3mo, 6mo, 1y, 2y, 5y, 10y, ytd, max)
        
        Returns:
            DataFrame with historical data
        """
        try:
            ticker = self.SUPPORTED_PAIRS.get(currency_pair)
            if not ticker:
                raise ValueError(f"Unsupported currency pair: {currency_pair}")
            
            # Run yfinance download in thread pool
            loop = asyncio.get_event_loop()
            
            if start_date and end_date:
                data = await loop.run_in_executor(
                    None,
                    lambda: yf.download(ticker, start=start_date, end=end_date, progress=False)
                )
            else:
                data = await loop.run_in_executor(
                    None,
                    lambda: yf.download(ticker, period=period, progress=False)
                )
            
            if data.empty:
                logger.warning(f"No data fetched for {currency_pair}")
                return pd.DataFrame()
            
            # Add currency pair column
            data['currency_pair'] = currency_pair
            
            logger.info(f"Fetched {len(data)} records for {currency_pair}")
            return data
            
        except Exception as e:
            logger.error(f"Error fetching historical data: {str(e)}")
            raise
    
    async def save_to_database(
        self,
        db: AsyncSession,
        data: pd.DataFrame,
        currency_pair: str
    ) -> int:
        """
        Save historical data to database
        
        Args:
            db: Database session
            data: DataFrame with historical data
            currency_pair: Currency pair
        
        Returns:
            Number of records saved
        """
        try:
            records_saved = 0
            
            for index, row in data.iterrows():
                # Check if record already exists
                existing = await db.execute(
                    select(ExchangeRate).where(
                        ExchangeRate.date == index.date()
                    )
                )
                
                if existing.scalar_one_or_none():
                    continue
                
                # Create new record
                exchange_rate = ExchangeRate(
                    date=index.date(),
                    open_rate=float(row['Open']),
                    high_rate=float(row['High']),
                    low_rate=float(row['Low']),
                    close_rate=float(row['Close']),
                    volume=int(row['Volume']) if 'Volume' in row and row['Volume'] else None,
                    source=self.source,
                    is_holiday=False,
                    is_interpolated=False
                )
                
                db.add(exchange_rate)
                records_saved += 1
            
            await db.commit()
            logger.info(f"Saved {records_saved} new records to database")
            return records_saved
            
        except Exception as e:
            await db.rollback()
            logger.error(f"Error saving to database: {str(e)}")
            raise
    
    async def fetch_and_save(
        self,
        db: AsyncSession,
        currency_pair: str = 'USD/JPY',
        period: str = '1y'
    ) -> Dict[str, Any]:
        """
        Fetch historical data and save to database
        
        Args:
            db: Database session
            currency_pair: Currency pair
            period: Period for historical data
        
        Returns:
            Summary of operation
        """
        try:
            # Fetch data
            data = await self.fetch_historical_data(
                currency_pair=currency_pair,
                period=period
            )
            
            if data.empty:
                return {
                    'status': 'no_data',
                    'message': f'No data available for {currency_pair}',
                    'records_fetched': 0,
                    'records_saved': 0
                }
            
            # Save to database
            records_saved = await self.save_to_database(db, data, currency_pair)
            
            return {
                'status': 'success',
                'message': f'Successfully fetched and saved historical data for {currency_pair}',
                'records_fetched': len(data),
                'records_saved': records_saved,
                'date_range': {
                    'start': data.index[0].strftime('%Y-%m-%d'),
                    'end': data.index[-1].strftime('%Y-%m-%d')
                }
            }
            
        except Exception as e:
            logger.error(f"Error in fetch_and_save: {str(e)}")
            return {
                'status': 'error',
                'message': str(e),
                'records_fetched': 0,
                'records_saved': 0
            }
    
    async def fetch_multiple_pairs(
        self,
        db: AsyncSession,
        currency_pairs: Optional[List[str]] = None,
        period: str = '1y'
    ) -> List[Dict[str, Any]]:
        """
        Fetch historical data for multiple currency pairs
        
        Args:
            db: Database session
            currency_pairs: List of currency pairs (defaults to all supported)
            period: Period for historical data
        
        Returns:
            List of operation summaries
        """
        if currency_pairs is None:
            currency_pairs = list(self.SUPPORTED_PAIRS.keys())
        
        results = []
        for pair in currency_pairs:
            logger.info(f"Fetching historical data for {pair}")
            result = await self.fetch_and_save(db, pair, period)
            results.append({
                'currency_pair': pair,
                **result
            })
            
            # Small delay to avoid rate limiting
            await asyncio.sleep(1)
        
        return results
    
    async def get_data_summary(
        self,
        db: AsyncSession,
        currency_pair: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Get summary of available historical data
        
        Args:
            db: Database session
            currency_pair: Optional specific currency pair
        
        Returns:
            Summary of available data
        """
        try:
            query = select(ExchangeRate).where(
                ExchangeRate.source == DataSourceType.YFINANCE
            )
            
            # Note: ExchangeRateモデルにはcurrency_pairフィールドがないため、
            # USD/JPYデータのみを扱う前提とする
            
            result = await db.execute(query)
            records = result.scalars().all()
            
            if not records:
                return {
                    'total_records': 0,
                    'currency_pairs': [],
                    'date_range': None
                }
            
            # USD/JPYのみとして集計
            min_date = min(record.date for record in records)
            max_date = max(record.date for record in records)
            
            return {
                'total_records': len(records),
                'currency_pairs': [
                    {
                        'pair': 'USD/JPY',
                        'count': len(records),
                        'date_range': {
                            'start': min_date.strftime('%Y-%m-%d'),
                            'end': max_date.strftime('%Y-%m-%d')
                        }
                    }
                ]
            }
            
        except Exception as e:
            logger.error(f"Error getting data summary: {str(e)}")
            raise