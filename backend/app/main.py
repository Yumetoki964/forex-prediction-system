"""
Forex Prediction System - Main FastAPI Application
==================================================

CHAIN-001連鎖APIテスト用のFastAPIアプリケーション
エンドポイント連鎖：4.2→1.1→1.2→1.3
"""

from fastapi import FastAPI, HTTPException, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
import os
import asyncio
import json
from datetime import datetime

# Import routers
from .routers.data import router as data_router
from .routers.rates import router as rates_router
from .api.endpoints.backtest import router as backtest_router
from .api.endpoints.predictions import router as predictions_router
from .api.endpoints.signals import router as signals_router
from .routers.auth_simple import router as auth_router
from .routers.alerts import router as alerts_router
from .routers.metrics import router as metrics_router
from .api.endpoints.charts import router as charts_router
from .api.endpoints.indicators import router as indicators_router

# Create FastAPI instance
app = FastAPI(
    title="Forex Prediction System",
    description="為替予測システムのAPIエンドポイント",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:5173", "http://127.0.0.1:5173", "http://localhost:3173", "http://127.0.0.1:3173", "http://localhost:8000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers with API prefix
app.include_router(auth_router, tags=["authentication"])  # auth_router already has /api/auth prefix
app.include_router(data_router, prefix="/api/data", tags=["data"])
app.include_router(rates_router, prefix="/api/rates", tags=["rates"]) 
app.include_router(backtest_router, prefix="/api/backtest", tags=["backtest"])
app.include_router(predictions_router, prefix="/api/predictions", tags=["predictions"])
app.include_router(signals_router, prefix="/api/signals", tags=["signals"])
app.include_router(alerts_router, prefix="/api/alerts", tags=["alerts"])
app.include_router(metrics_router, prefix="/api/metrics", tags=["metrics"])
app.include_router(charts_router, prefix="/api/charts", tags=["charts"])
app.include_router(indicators_router, prefix="/api/indicators", tags=["indicators"])


@app.get("/")
async def root():
    """ヘルスチェック用ルートエンドポイント"""
    return {
        "message": "Forex Prediction System API",
        "version": "1.0.0",
        "status": "running",
        "chain_endpoints": {
            "4.2": "/api/data/collect",
            "1.1": "/api/rates/current", 
            "1.2": "/api/predictions/latest",
            "1.3": "/api/signals/current",
            "2.1": "/api/charts/historical",
            "2.2": "/api/predictions/detailed",
            "2.3": "/api/indicators/technical",
            "2.4": "/api/indicators/economic",
            "3.1": "/api/backtest/run",
            "3.2": "/api/backtest/results/{job_id}",
            "3.3": "/api/backtest/metrics/{job_id}",
            "3.4": "/api/backtest/trades/{job_id}"
        }
    }


@app.get("/health")
@app.get("/api/health")
async def health_check():
    """詳細ヘルスチェック"""
    return {
        "status": "healthy",
        "database": "connected",
        "services": {
            "data": "operational",
            "rates": "operational", 
            "predictions": "operational",
            "signals": "operational"
        },
        "chain_001_ready": True
    }


# WebSocketエンドポイント
from .websocket.manager import manager, generate_mock_price_data, generate_mock_signals, generate_mock_alerts

@app.websocket("/ws/{client_id}")
async def websocket_endpoint(websocket: WebSocket, client_id: str):
    """WebSocket接続エンドポイント"""
    await manager.connect(websocket)
    
    # クライアントをデフォルトトピックに登録
    manager.subscribe(websocket, "rates")
    manager.subscribe(websocket, "signals")
    manager.subscribe(websocket, "alerts")
    
    try:
        await websocket.send_text(json.dumps({
            "type": "connection",
            "message": f"Connected as {client_id}",
            "timestamp": datetime.now().isoformat()
        }))
        
        while True:
            # クライアントからのメッセージを待機
            data = await websocket.receive_text()
            message = json.loads(data)
            
            # サブスクリプション管理
            if message.get("type") == "subscribe":
                topic = message.get("topic")
                if topic:
                    manager.subscribe(websocket, topic)
                    await websocket.send_text(json.dumps({
                        "type": "subscribed",
                        "topic": topic
                    }))
            elif message.get("type") == "unsubscribe":
                topic = message.get("topic")
                if topic:
                    manager.unsubscribe(websocket, topic)
                    await websocket.send_text(json.dumps({
                        "type": "unsubscribed",
                        "topic": topic
                    }))
            else:
                # エコーバック
                await websocket.send_text(f"Echo: {data}")
                
    except WebSocketDisconnect:
        manager.disconnect(websocket)
        await manager.broadcast(json.dumps({
            "type": "disconnection",
            "message": f"Client {client_id} disconnected"
        }))

# WebSocket用のバックグラウンドタスクを開始
@app.on_event("startup")
async def startup_event():
    """アプリケーション起動時のイベント"""
    # バックグラウンドでデータ生成タスクを開始
    asyncio.create_task(generate_mock_price_data())
    asyncio.create_task(generate_mock_signals())
    asyncio.create_task(generate_mock_alerts())


if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("API_PORT", 8173))
    uvicorn.run(app, host="0.0.0.0", port=port, reload=True)