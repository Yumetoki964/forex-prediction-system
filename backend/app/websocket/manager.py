"""
WebSocket接続マネージャー
"""
from typing import List, Dict
from fastapi import WebSocket
import json
import asyncio
from datetime import datetime
import random

class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []
        self.subscriptions: Dict[str, List[WebSocket]] = {}
        
    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)
        
    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)
        # Remove from all subscriptions
        for topic in self.subscriptions:
            if websocket in self.subscriptions[topic]:
                self.subscriptions[topic].remove(websocket)
    
    def subscribe(self, websocket: WebSocket, topic: str):
        if topic not in self.subscriptions:
            self.subscriptions[topic] = []
        if websocket not in self.subscriptions[topic]:
            self.subscriptions[topic].append(websocket)
    
    def unsubscribe(self, websocket: WebSocket, topic: str):
        if topic in self.subscriptions and websocket in self.subscriptions[topic]:
            self.subscriptions[topic].remove(websocket)
    
    async def send_personal_message(self, message: str, websocket: WebSocket):
        await websocket.send_text(message)
    
    async def broadcast(self, message: str):
        for connection in self.active_connections:
            try:
                await connection.send_text(message)
            except:
                # Connection might be closed
                pass
    
    async def broadcast_to_topic(self, topic: str, message: str):
        if topic in self.subscriptions:
            for connection in self.subscriptions[topic]:
                try:
                    await connection.send_text(message)
                except:
                    # Connection might be closed
                    pass

manager = ConnectionManager()

async def generate_mock_price_data():
    """模擬価格データを生成"""
    base_prices = {
        "USDJPY": 150.25,
        "EURUSD": 1.0850,
        "GBPUSD": 1.2650,
        "AUDUSD": 0.6550
    }
    
    while True:
        for pair, base_price in base_prices.items():
            # ランダムな価格変動を生成
            change = random.uniform(-0.01, 0.01)
            new_price = base_price + change
            base_prices[pair] = new_price
            
            data = {
                "type": "price_update",
                "pair": pair,
                "price": round(new_price, 4),
                "timestamp": datetime.now().isoformat(),
                "change": round(change, 4),
                "change_percent": round((change / base_price) * 100, 2)
            }
            
            # 価格更新をブロードキャスト
            await manager.broadcast_to_topic("rates", json.dumps(data))
        
        await asyncio.sleep(2)  # 2秒ごとに更新

async def generate_mock_signals():
    """模擬シグナルを生成"""
    signals = ["BUY", "SELL", "HOLD"]
    pairs = ["USDJPY", "EURUSD", "GBPUSD", "AUDUSD"]
    
    while True:
        await asyncio.sleep(10)  # 10秒ごとにシグナル
        
        pair = random.choice(pairs)
        signal = random.choice(signals)
        strength = random.randint(60, 95)
        
        data = {
            "type": "signal_update",
            "pair": pair,
            "signal": signal,
            "strength": strength,
            "timestamp": datetime.now().isoformat(),
            "reason": f"Technical analysis indicates {signal} opportunity"
        }
        
        await manager.broadcast_to_topic("signals", json.dumps(data))

async def generate_mock_alerts():
    """模擬アラートを生成"""
    alert_types = [
        {"type": "price", "message": "Price threshold reached"},
        {"type": "news", "message": "Important economic news"},
        {"type": "signal", "message": "Strong trading signal detected"}
    ]
    
    while True:
        await asyncio.sleep(30)  # 30秒ごとにアラート
        
        alert = random.choice(alert_types)
        
        data = {
            "type": "alert",
            "alert_type": alert["type"],
            "message": alert["message"],
            "severity": random.choice(["info", "warning", "critical"]),
            "timestamp": datetime.now().isoformat()
        }
        
        await manager.broadcast_to_topic("alerts", json.dumps(data))