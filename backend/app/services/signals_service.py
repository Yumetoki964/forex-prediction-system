"""
Forex Prediction System - Trading Signals Service
================================================

売買シグナル関連のビジネスロジック実装
5段階売買判定（強い売り〜強い買い）とシグナル生成機能
"""

from datetime import datetime, date, timedelta
from decimal import Decimal
from typing import Optional, Dict, Any, List
import json
import logging
from sqlalchemy import select, desc, and_, func
from sqlalchemy.ext.asyncio import AsyncSession

from ..models import (
    TradingSignal, SignalType, ExchangeRate, Prediction, 
    TechnicalIndicator, PredictionPeriod
)
from ..schemas.signals import (
    TradingSignalResponse, TradingSignalCreate,
    CurrentSignalResponse
)

logger = logging.getLogger(__name__)


class SignalsService:
    """売買シグナルサービス"""
    
    def __init__(self, db: AsyncSession):
        self.db = db
    
    # ===================================================================
    # 基本CRUD操作
    # ===================================================================
    
    async def get_all(self, skip: int = 0, limit: int = 100) -> List[TradingSignalResponse]:
        """全売買シグナルを取得"""
        stmt = (
            select(TradingSignal)
            .order_by(desc(TradingSignal.date))
            .offset(skip)
            .limit(limit)
        )
        result = await self.db.execute(stmt)
        signals = result.scalars().all()
        
        return [
            TradingSignalResponse.model_validate(signal) 
            for signal in signals
        ]
    
    async def get_by_id(self, signal_id: int) -> Optional[TradingSignalResponse]:
        """IDで売買シグナルを取得"""
        stmt = select(TradingSignal).where(TradingSignal.id == signal_id)
        result = await self.db.execute(stmt)
        signal = result.scalar_one_or_none()
        
        if signal:
            return TradingSignalResponse.model_validate(signal)
        return None
    
    async def get_by_date(self, target_date: date) -> Optional[TradingSignalResponse]:
        """日付で売買シグナルを取得"""
        stmt = select(TradingSignal).where(TradingSignal.date == target_date)
        result = await self.db.execute(stmt)
        signal = result.scalar_one_or_none()
        
        if signal:
            return TradingSignalResponse.model_validate(signal)
        return None
    
    async def create(self, data: TradingSignalCreate) -> TradingSignalResponse:
        """売買シグナルを作成"""
        signal = TradingSignal(**data.model_dump())
        self.db.add(signal)
        await self.db.commit()
        await self.db.refresh(signal)
        
        return TradingSignalResponse.model_validate(signal)
    
    # ===================================================================
    # ビジネスロジック実装
    # ===================================================================
    
    async def get_current_signal(self) -> CurrentSignalResponse:
        """
        現在の売買シグナルを取得・生成
        
        最新のシグナルが存在しない場合は自動生成する
        前回シグナルからの変化も検出して返す
        """
        today = date.today()
        
        # 最新のシグナルを取得
        current_signal = await self._get_or_generate_latest_signal()
        
        # 前回シグナルを取得（比較用）
        previous_signal = await self._get_previous_signal(current_signal.date)
        
        # シグナル変化を検出
        signal_changed = (
            previous_signal is None or 
            current_signal.signal_type != previous_signal.signal_type
        )
        
        # UI表示用情報を生成
        display_text = self._get_signal_display_text(current_signal.signal_type)
        color_code = self._get_signal_color(current_signal.signal_type)
        trend_arrow = self._get_trend_arrow(current_signal.signal_type, current_signal.strength)
        
        # 次回更新時刻（明日朝7時）
        next_update = datetime.now().replace(hour=7, minute=0, second=0, microsecond=0)
        if next_update <= datetime.now():
            next_update += timedelta(days=1)
        
        return CurrentSignalResponse(
            signal=current_signal,
            previous_signal=previous_signal.signal_type if previous_signal else None,
            signal_changed=signal_changed,
            display_text=display_text,
            color_code=color_code,
            trend_arrow=trend_arrow,
            last_updated=datetime.now(),
            next_update_at=next_update
        )
    
    async def _get_or_generate_latest_signal(self) -> TradingSignalResponse:
        """最新シグナルを取得または生成"""
        # 今日のシグナルを確認
        today = date.today()
        today_signal = await self.get_by_date(today)
        
        if today_signal:
            return today_signal
        
        # 今日のシグナルがない場合は生成
        logger.info(f"今日（{today}）のシグナルが未生成のため、自動生成を開始")
        return await self._generate_daily_signal(today)
    
    async def _get_previous_signal(self, current_date: date) -> Optional[TradingSignal]:
        """前回のシグナルを取得"""
        stmt = (
            select(TradingSignal)
            .where(TradingSignal.date < current_date)
            .order_by(desc(TradingSignal.date))
            .limit(1)
        )
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()
    
    async def _generate_daily_signal(self, target_date: date) -> TradingSignalResponse:
        """
        指定日の売買シグナルを自動生成
        
        1. 最新の為替レートを取得
        2. テクニカル指標を分析
        3. 予測データを評価
        4. 統合シグナルを生成
        """
        # 最新の為替レートを取得
        current_rate = await self._get_latest_rate()
        if not current_rate:
            raise ValueError("売買シグナル生成に必要な為替レートデータが不足しています")
        
        # テクニカル分析スコアを計算
        technical_score = await self._calculate_technical_score(target_date)
        
        # 予測分析スコアを計算
        prediction_score, prediction_id = await self._calculate_prediction_score(target_date)
        
        # 統合シグナルを生成
        signal_type, confidence, strength = self._generate_integrated_signal(
            technical_score, prediction_score
        )
        
        # 根拠情報を作成
        reasoning = self._create_reasoning(
            technical_score=technical_score,
            prediction_score=prediction_score,
            current_rate=Decimal(str(current_rate.close_rate))
        )
        
        # シグナルを作成・保存
        signal_data = TradingSignalCreate(
            date=target_date,
            signal_type=signal_type,
            confidence=confidence,
            strength=strength,
            reasoning=reasoning,
            technical_score=technical_score,
            prediction_score=prediction_score,
            prediction_id=prediction_id,
            current_rate=Decimal(str(current_rate.close_rate))
        )
        
        created_signal = await self.create(signal_data)
        logger.info(f"売買シグナルを生成しました: {target_date} - {signal_type.value}")
        
        return created_signal
    
    async def _get_latest_rate(self) -> Optional[ExchangeRate]:
        """最新の為替レートを取得"""
        stmt = (
            select(ExchangeRate)
            .order_by(desc(ExchangeRate.date))
            .limit(1)
        )
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()
    
    async def _calculate_technical_score(self, target_date: date) -> float:
        """
        テクニカル分析スコアを計算
        
        RSI、MACD、移動平均などの指標を統合して-1.0〜1.0のスコアを生成
        -1.0: 強い売りシグナル、1.0: 強い買いシグナル
        """
        # 最新のテクニカル指標を取得
        stmt = (
            select(TechnicalIndicator)
            .order_by(desc(TechnicalIndicator.date))
            .limit(1)
        )
        result = await self.db.execute(stmt)
        indicator = result.scalar_one_or_none()
        
        if not indicator:
            # テクニカル指標がない場合はニュートラル
            logger.warning("テクニカル指標データが不足しています")
            return 0.0
        
        score = 0.0
        weight_sum = 0.0
        
        # RSI分析（重み: 0.3）
        if indicator.rsi_14 is not None:
            rsi_score = self._analyze_rsi(float(indicator.rsi_14))
            score += rsi_score * 0.3
            weight_sum += 0.3
        
        # MACD分析（重み: 0.3）
        if indicator.macd is not None and indicator.macd_signal is not None:
            macd_score = self._analyze_macd(
                float(indicator.macd), 
                float(indicator.macd_signal)
            )
            score += macd_score * 0.3
            weight_sum += 0.3
        
        # 移動平均分析（重み: 0.2）
        if indicator.sma_5 is not None and indicator.sma_25 is not None:
            ma_score = self._analyze_moving_average(
                float(indicator.sma_5), 
                float(indicator.sma_25)
            )
            score += ma_score * 0.2
            weight_sum += 0.2
        
        # ボリンジャーバンド分析（重み: 0.2）
        if (indicator.bb_upper is not None and 
            indicator.bb_lower is not None and 
            indicator.bb_middle is not None):
            bb_score = self._analyze_bollinger_bands(
                float(indicator.bb_upper),
                float(indicator.bb_middle), 
                float(indicator.bb_lower)
            )
            score += bb_score * 0.2
            weight_sum += 0.2
        
        # 正規化
        if weight_sum > 0:
            score = score / weight_sum
        
        # -1.0〜1.0の範囲に制限
        return max(-1.0, min(1.0, score))
    
    async def _calculate_prediction_score(self, target_date: date) -> tuple[float, Optional[int]]:
        """
        予測分析スコアを計算
        
        最新の予測データから将来のトレンド方向性を評価
        戻り値: (スコア(-1.0〜1.0), 関連予測ID)
        """
        # 最新の予測データを取得（1週間予測を優先）
        stmt = (
            select(Prediction)
            .where(Prediction.prediction_date <= target_date)
            .where(Prediction.period == PredictionPeriod.ONE_WEEK)
            .order_by(desc(Prediction.prediction_date))
            .limit(1)
        )
        result = await self.db.execute(stmt)
        prediction = result.scalar_one_or_none()
        
        if not prediction:
            logger.warning("予測データが不足しています")
            return 0.0, None
        
        # 現在レートを取得
        current_rate = await self._get_latest_rate()
        if not current_rate:
            return 0.0, prediction.id
        
        # 予測変化率を計算
        current_price = float(current_rate.close_rate)
        predicted_price = float(prediction.predicted_rate)
        change_rate = (predicted_price - current_price) / current_price
        
        # 予測強度を考慮したスコア計算
        base_score = change_rate * 100  # パーセンテージに変換
        confidence_weight = prediction.prediction_strength
        
        # スコア調整（-1.0〜1.0の範囲）
        score = base_score * confidence_weight
        score = max(-1.0, min(1.0, score))
        
        return score, prediction.id
    
    def _generate_integrated_signal(
        self, 
        technical_score: float, 
        prediction_score: float
    ) -> tuple[SignalType, float, float]:
        """
        テクニカルスコアと予測スコアを統合してシグナルを生成
        
        戻り値: (シグナル種別, 信頼度, 強度)
        """
        # 統合スコア計算（テクニカル60%、予測40%）
        integrated_score = technical_score * 0.6 + prediction_score * 0.4
        
        # 信頼度計算（両スコアの一致度で算出）
        score_agreement = 1.0 - abs(technical_score - prediction_score) / 2.0
        confidence = max(0.1, min(1.0, score_agreement * 0.8 + 0.2))
        
        # 強度計算（統合スコアの絶対値）
        strength = min(1.0, abs(integrated_score) * 1.5)
        
        # シグナル判定
        if integrated_score <= -0.6:
            signal_type = SignalType.STRONG_SELL
        elif integrated_score <= -0.2:
            signal_type = SignalType.SELL
        elif integrated_score < 0.2:
            signal_type = SignalType.HOLD
        elif integrated_score < 0.6:
            signal_type = SignalType.BUY
        else:
            signal_type = SignalType.STRONG_BUY
        
        return signal_type, confidence, strength
    
    # ===================================================================
    # テクニカル分析ヘルパー
    # ===================================================================
    
    def _analyze_rsi(self, rsi: float) -> float:
        """RSI分析（-1.0〜1.0のスコア）"""
        if rsi >= 70:
            return -0.8  # 売られ過ぎ
        elif rsi >= 60:
            return -0.3
        elif rsi >= 40:
            return 0.0   # ニュートラル
        elif rsi >= 30:
            return 0.3
        else:
            return 0.8   # 買われ過ぎ
    
    def _analyze_macd(self, macd: float, signal: float) -> float:
        """MACD分析（-1.0〜1.0のスコア）"""
        diff = macd - signal
        if diff > 0.01:
            return 0.7   # 強い上昇トレンド
        elif diff > 0.005:
            return 0.3
        elif diff > -0.005:
            return 0.0   # ニュートラル
        elif diff > -0.01:
            return -0.3
        else:
            return -0.7  # 強い下降トレンド
    
    def _analyze_moving_average(self, sma_5: float, sma_25: float) -> float:
        """移動平均分析（-1.0〜1.0のスコア）"""
        ratio = sma_5 / sma_25
        if ratio >= 1.005:
            return 0.6   # 短期が長期を大きく上回る
        elif ratio >= 1.002:
            return 0.3
        elif ratio >= 0.998:
            return 0.0   # ニュートラル
        elif ratio >= 0.995:
            return -0.3
        else:
            return -0.6  # 短期が長期を大きく下回る
    
    def _analyze_bollinger_bands(
        self, 
        upper: float, 
        middle: float, 
        lower: float
    ) -> float:
        """ボリンジャーバンド分析（-1.0〜1.0のスコア）"""
        # 現在レートを取得（簡略化：中央値を現在値として扱う）
        current_rate = middle
        
        # バンド内での位置を計算
        band_width = upper - lower
        if band_width <= 0:
            return 0.0
        
        position = (current_rate - lower) / band_width
        
        if position >= 0.8:
            return -0.5  # 上限近く（売りシグナル）
        elif position <= 0.2:
            return 0.5   # 下限近く（買いシグナル）
        else:
            return 0.0   # 中央付近
    
    def _create_reasoning(
        self, 
        technical_score: float, 
        prediction_score: float, 
        current_rate: Decimal
    ) -> str:
        """シグナル根拠情報をJSON形式で作成"""
        reasoning_data = {
            "technical_analysis": {
                "score": round(technical_score, 3),
                "indicators_used": ["RSI", "MACD", "Moving Averages", "Bollinger Bands"],
                "signal_strength": "strong" if abs(technical_score) > 0.6 else "moderate"
            },
            "prediction_analysis": {
                "score": round(prediction_score, 3),
                "forecast_period": "1 week",
                "confidence_level": "high" if abs(prediction_score) > 0.5 else "medium"
            },
            "market_context": {
                "current_rate": float(current_rate),
                "analysis_timestamp": datetime.now().isoformat()
            }
        }
        
        return json.dumps(reasoning_data, ensure_ascii=False)
    
    # ===================================================================
    # UI表示ヘルパー
    # ===================================================================
    
    def _get_signal_display_text(self, signal_type: SignalType) -> str:
        """シグナル表示テキストを生成"""
        display_map = {
            SignalType.STRONG_SELL: "強い売りシグナル",
            SignalType.SELL: "売りシグナル",
            SignalType.HOLD: "様子見",
            SignalType.BUY: "買いシグナル",
            SignalType.STRONG_BUY: "強い買いシグナル"
        }
        return display_map.get(signal_type, "不明")
    
    def _get_signal_color(self, signal_type: SignalType) -> str:
        """シグナル色を生成"""
        color_map = {
            SignalType.STRONG_SELL: "#D32F2F",  # 濃い赤
            SignalType.SELL: "#F44336",         # 赤
            SignalType.HOLD: "#FF9800",         # オレンジ
            SignalType.BUY: "#4CAF50",          # 緑
            SignalType.STRONG_BUY: "#2E7D32"    # 濃い緑
        }
        return color_map.get(signal_type, "#9E9E9E")
    
    def _get_trend_arrow(self, signal_type: SignalType, strength: float) -> str:
        """トレンド矢印を生成"""
        if signal_type in [SignalType.STRONG_SELL, SignalType.SELL]:
            return "↓↓" if strength > 0.7 else "↓"
        elif signal_type in [SignalType.STRONG_BUY, SignalType.BUY]:
            return "↑↑" if strength > 0.7 else "↑"
        else:
            return "→"