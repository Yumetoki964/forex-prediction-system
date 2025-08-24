"""
為替レートWebスクレイピングサービス
"""

import aiohttp
from bs4 import BeautifulSoup
from typing import Optional, Dict, List
from datetime import datetime
import re
import asyncio

class ForexScraper:
    """為替レートをWebサイトから取得するクラス"""
    
    def __init__(self):
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
    
    async def get_rate_from_xe(self) -> Optional[Dict]:
        """
        XE.comから為替レートを取得
        """
        try:
            url = "https://www.xe.com/currencyconverter/convert/?Amount=1&From=USD&To=JPY"
            
            async with aiohttp.ClientSession() as session:
                async with session.get(url, headers=self.headers) as response:
                    if response.status == 200:
                        html = await response.text()
                        soup = BeautifulSoup(html, 'html.parser')
                        
                        # XE.comのレート表示部分を探す
                        rate_element = soup.find('p', class_='result__BigRate-sc-1bsijpp-1')
                        if rate_element:
                            rate_text = rate_element.text.strip()
                            # 数値部分を抽出
                            rate_match = re.search(r'([\d,]+\.?\d*)', rate_text)
                            if rate_match:
                                rate = float(rate_match.group(1).replace(',', ''))
                                return {
                                    'source': 'XE.com',
                                    'rate': rate,
                                    'timestamp': datetime.now(),
                                    'currency_pair': 'USD/JPY'
                                }
        except Exception as e:
            print(f"XE.com scraping error: {e}")
        return None
    
    async def get_rate_from_google(self) -> Optional[Dict]:
        """
        Google検索結果から為替レートを取得
        """
        try:
            url = "https://www.google.com/search?q=1+USD+to+JPY"
            
            async with aiohttp.ClientSession() as session:
                async with session.get(url, headers=self.headers) as response:
                    if response.status == 200:
                        html = await response.text()
                        soup = BeautifulSoup(html, 'html.parser')
                        
                        # Googleの為替レート表示部分を探す
                        # 構造は変更される可能性があるため、複数のパターンを試す
                        patterns = [
                            {'class': 'DFlfde'},
                            {'class': 'SwHCTb'},
                            {'data-precision': '2'}
                        ]
                        
                        for pattern in patterns:
                            rate_element = soup.find('span', pattern)
                            if rate_element:
                                rate_text = rate_element.text.strip()
                                rate_match = re.search(r'([\d,]+\.?\d*)', rate_text)
                                if rate_match:
                                    rate = float(rate_match.group(1).replace(',', ''))
                                    return {
                                        'source': 'Google',
                                        'rate': rate,
                                        'timestamp': datetime.now(),
                                        'currency_pair': 'USD/JPY'
                                    }
        except Exception as e:
            print(f"Google scraping error: {e}")
        return None
    
    async def get_rate_from_yahoo_finance(self) -> Optional[Dict]:
        """
        Yahoo Financeから為替レートを取得
        """
        try:
            url = "https://finance.yahoo.com/quote/USDJPY=X"
            
            async with aiohttp.ClientSession() as session:
                async with session.get(url, headers=self.headers) as response:
                    if response.status == 200:
                        html = await response.text()
                        soup = BeautifulSoup(html, 'html.parser')
                        
                        # Yahoo Financeの価格表示部分を探す
                        price_element = soup.find('fin-streamer', {'data-symbol': 'USDJPY=X'})
                        if not price_element:
                            # 別のパターンを試す
                            price_element = soup.find('span', {'data-reactid': '32'})
                        
                        if price_element:
                            rate_text = price_element.text.strip()
                            rate_match = re.search(r'([\d,]+\.?\d*)', rate_text)
                            if rate_match:
                                rate = float(rate_match.group(1).replace(',', ''))
                                return {
                                    'source': 'Yahoo Finance',
                                    'rate': rate,
                                    'timestamp': datetime.now(),
                                    'currency_pair': 'USD/JPY'
                                }
        except Exception as e:
            print(f"Yahoo Finance scraping error: {e}")
        return None
    
    async def get_rate_from_investing(self) -> Optional[Dict]:
        """
        Investing.comから為替レートを取得
        """
        try:
            url = "https://www.investing.com/currencies/usd-jpy"
            
            async with aiohttp.ClientSession() as session:
                async with session.get(url, headers=self.headers) as response:
                    if response.status == 200:
                        html = await response.text()
                        soup = BeautifulSoup(html, 'html.parser')
                        
                        # Investing.comの価格表示部分を探す
                        price_element = soup.find('span', {'data-test': 'instrument-price-last'})
                        if not price_element:
                            price_element = soup.find('span', class_='text-2xl')
                        
                        if price_element:
                            rate_text = price_element.text.strip()
                            rate_match = re.search(r'([\d,]+\.?\d*)', rate_text)
                            if rate_match:
                                rate = float(rate_match.group(1).replace(',', ''))
                                return {
                                    'source': 'Investing.com',
                                    'rate': rate,
                                    'timestamp': datetime.now(),
                                    'currency_pair': 'USD/JPY'
                                }
        except Exception as e:
            print(f"Investing.com scraping error: {e}")
        return None
    
    async def get_current_rate(self) -> Dict:
        """
        複数のソースから為替レートを取得（フォールバック付き）
        """
        # 各ソースを順番に試す
        sources = [
            self.get_rate_from_yahoo_finance,
            self.get_rate_from_google,
            self.get_rate_from_xe,
            self.get_rate_from_investing,
        ]
        
        for source_func in sources:
            result = await source_func()
            if result:
                return result
        
        # すべて失敗した場合はデモデータを返す
        return {
            'source': 'Demo',
            'rate': 149.85,
            'timestamp': datetime.now(),
            'currency_pair': 'USD/JPY',
            'error': 'All sources failed, returning demo data'
        }
    
    async def get_multiple_rates(self) -> List[Dict]:
        """
        複数のソースから並行してレートを取得
        """
        tasks = [
            self.get_rate_from_yahoo_finance(),
            self.get_rate_from_google(),
            self.get_rate_from_xe(),
            self.get_rate_from_investing(),
        ]
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # 成功した結果のみをフィルタリング
        valid_results = []
        for result in results:
            if isinstance(result, dict) and result:
                valid_results.append(result)
        
        return valid_results if valid_results else [{
            'source': 'Demo',
            'rate': 149.85,
            'timestamp': datetime.now(),
            'currency_pair': 'USD/JPY',
            'error': 'All sources failed, returning demo data'
        }]