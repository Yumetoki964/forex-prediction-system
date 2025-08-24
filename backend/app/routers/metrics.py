"""
メトリクス（指標）エンドポイント
"""
from fastapi import APIRouter, HTTPException
from typing import List, Dict, Any
from datetime import datetime, timedelta
from pydantic import BaseModel
import random

router = APIRouter()

class RiskMetrics(BaseModel):
    overall_risk: str  # 'low', 'medium', 'high'
    risk_score: float  # 0-100
    var_95: float  # Value at Risk 95%
    var_99: float  # Value at Risk 99%
    max_drawdown: float
    sharpe_ratio: float
    win_rate: float
    risk_factors: List[Dict[str, Any]]

class PerformanceMetrics(BaseModel):
    total_return: float
    monthly_return: float
    daily_return: float
    total_trades: int
    winning_trades: int
    losing_trades: int
    average_win: float
    average_loss: float
    profit_factor: float

@router.get("/risk", response_model=RiskMetrics)
async def get_risk_metrics():
    """リスク指標を取得"""
    return RiskMetrics(
        overall_risk="medium",
        risk_score=65.5,
        var_95=2.5,
        var_99=3.8,
        max_drawdown=12.3,
        sharpe_ratio=1.45,
        win_rate=58.5,
        risk_factors=[
            {"name": "市場ボラティリティ", "level": "high", "impact": 0.35},
            {"name": "ポジションサイズ", "level": "medium", "impact": 0.25},
            {"name": "相関リスク", "level": "low", "impact": 0.15},
            {"name": "流動性リスク", "level": "low", "impact": 0.10}
        ]
    )

@router.get("/performance", response_model=PerformanceMetrics)
async def get_performance_metrics():
    """パフォーマンス指標を取得"""
    return PerformanceMetrics(
        total_return=15.7,
        monthly_return=2.3,
        daily_return=0.12,
        total_trades=147,
        winning_trades=86,
        losing_trades=61,
        average_win=125.50,
        average_loss=87.30,
        profit_factor=1.43
    )

@router.get("/historical")
async def get_historical_metrics(period: str = "1m"):
    """過去のメトリクスデータを取得"""
    
    # 期間に応じたデータポイント数を決定
    if period == "1d":
        points = 24
    elif period == "1w":
        points = 7
    elif period == "1m":
        points = 30
    else:
        points = 90
    
    # ダミーデータ生成
    data = []
    base_return = 100
    for i in range(points):
        base_return *= (1 + random.uniform(-0.02, 0.03))
        data.append({
            "date": (datetime.now() - timedelta(days=points-i)).isoformat(),
            "return": round(base_return - 100, 2),
            "risk_score": round(random.uniform(40, 80), 1),
            "trades": random.randint(3, 15),
            "win_rate": round(random.uniform(45, 65), 1)
        })
    
    return {
        "period": period,
        "data": data,
        "summary": {
            "avg_return": round(sum(d["return"] for d in data) / len(data), 2),
            "avg_risk": round(sum(d["risk_score"] for d in data) / len(data), 1),
            "total_trades": sum(d["trades"] for d in data),
            "avg_win_rate": round(sum(d["win_rate"] for d in data) / len(data), 1)
        }
    }

@router.get("/portfolio")
async def get_portfolio_metrics():
    """ポートフォリオ全体のメトリクス"""
    return {
        "total_value": 1000000,
        "available_balance": 250000,
        "positions_value": 750000,
        "unrealized_pnl": 12500,
        "realized_pnl": 45000,
        "margin_used": 150000,
        "margin_available": 100000,
        "leverage": 2.5,
        "currency_exposure": {
            "USD": 0.40,
            "EUR": 0.25,
            "JPY": 0.20,
            "GBP": 0.15
        }
    }

@router.get("/correlation")
async def get_correlation_matrix():
    """通貨ペア間の相関行列を取得"""
    pairs = ["USDJPY", "EURUSD", "GBPUSD", "AUDUSD"]
    matrix = {}
    
    for pair1 in pairs:
        matrix[pair1] = {}
        for pair2 in pairs:
            if pair1 == pair2:
                matrix[pair1][pair2] = 1.0
            else:
                # ランダムな相関係数を生成
                matrix[pair1][pair2] = round(random.uniform(-0.8, 0.8), 2)
    
    return {
        "pairs": pairs,
        "matrix": matrix,
        "strongest_positive": {"pair1": "EURUSD", "pair2": "GBPUSD", "correlation": 0.75},
        "strongest_negative": {"pair1": "USDJPY", "pair2": "EURUSD", "correlation": -0.62}
    }